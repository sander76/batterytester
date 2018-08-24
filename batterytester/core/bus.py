import asyncio
import logging
from asyncio import CancelledError
from enum import Enum

import aiohttp

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.helpers import FatalTestFailException, \
    TestSetupException
from batterytester.core.helpers.message_data import FatalData

LOGGER = logging.getLogger(__name__)


class BusState(Enum):
    undefined = 0
    setting_up = 1
    running = 2
    shutting_down = 3


class Bus:
    def __init__(self, loop=None):
        self.tasks = []
        self.test_runner_task = None
        self.running = True
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.exit_message = None
        self._data_handlers = []
        self.actors = {}
        self.sensors = []
        self.subscriptions = {}
        self._exception = None
        self._state = BusState.undefined

    #todo: Can this be removed ?
    @property
    def exception(self):
        return self._exception

    def register_data_handler(self, data_handler, test_name):
        """Registers a data handler"""
        data_handler.test_name = test_name
        self._data_handlers.append(data_handler)
        for _subscription in data_handler.get_subscriptions():
            _subj = _subscription[0]
            _handler = _subscription[1]
            if _subj in self.subscriptions:
                self.subscriptions[_subj].append(_handler)
            else:
                self.subscriptions[_subj] = [_handler]

    def notify(self, subject, data=None):
        """Notifies the data handlers for incoming data."""
        if subject in self.subscriptions:
            for _subscriber in self.subscriptions[subject]:
                try:
                    _subscriber(subject, data)
                except Exception as err:
                    raise

    def subscribe(self, subject, method):
        self.subscriptions[subject] = method

    def task_finished_callback(self, future):
        try:
            val = future.result()
            if val:
                print(val)
        except CancelledError:
            LOGGER.info("Catching a task cancellation.")
        except Exception as err:
            LOGGER.error("A background task has an error: {}".format(err))
            LOGGER.exception(err)
            self.notify(subj.TEST_FATAL, FatalData(err))
            """An exception is raised. Meaning one of the long running 
            tasks has encountered an error. Cancelling the main task and
            subsequently cancelling all other long running tasks."""
            if self._state == BusState.running:
                LOGGER.info("Forced stopping the test.")
                if self.test_runner_task:
                    self.test_runner_task.cancel()
            LOGGER.info("Bus state to shutting down.")
            self._state = BusState.shutting_down

    def add_async_task(self, coro):
        """Add an async task.

        The callback will be used to check whether these tasks do not
        exit prematurely. If so, the complete test will be stopped."""
        if not self._state == BusState.shutting_down:
            _task = self.loop.create_task(coro)
            _task.add_done_callback(self.task_finished_callback)
            self.tasks.append(_task)

    async def start_main_test(self, test_runner, test_name):
        self._state = BusState.setting_up

        LOGGER.info("Setting up handlers.")
        await asyncio.gather(
            *(_handler.setup(test_name, self) for _handler in
              self._data_handlers))
        LOGGER.info("Setting up actors.")
        await asyncio.gather(
            *(_actor.setup(test_name, self) for _actor in self.actors.values())
        )
        LOGGER.info("Setting up sensors.")
        await asyncio.gather(
            *(_sensor.setup(test_name, self) for _sensor in self.sensors)
        )
        LOGGER.info("Starting test runner.")
        if self._state == BusState.setting_up:
            self._state = BusState.running
            self.test_runner_task = asyncio.ensure_future(test_runner)

            await self.test_runner_task

    def _start_test(self, test_runner, test_name):
        try:
            self.loop.run_until_complete(
                self.start_main_test(test_runner, test_name))
        except TestSetupException as err:
            LOGGER.error(err)
            self._exception = err
        except CancelledError:
            LOGGER.error("Main test loop cancelled.")
        except FatalTestFailException as err:
            LOGGER.error("FATAL ERROR: {}".format(err))
            self.notify(subj.TEST_FATAL, FatalData(err))
        except KeyboardInterrupt:
            LOGGER.info("Test stopped due to keyboard interrupt.")
        except Exception as err:
            LOGGER.exception(err)
            self.notify(subj.TEST_FATAL, FatalData(err))
        finally:
            self.loop.run_until_complete(self.shutdown_test())

        return self.exit_message

    async def shutdown_test(self, message=None):
        # wait a little to have all tasks finish gracefully.
        LOGGER.info("stopping test")
        self._state = BusState.shutting_down
        await asyncio.sleep(1)


        if self.test_runner_task:
            LOGGER.info("stopping actual test")
            if not self.test_runner_task.done():
                self.test_runner_task.cancel()

        LOGGER.info("Shutting down data handlers")
        await asyncio.gather(
            *(_handler.shutdown(self) for _handler in
              self._data_handlers))
        LOGGER.info("Shutting down actors")
        await asyncio.gather(
            *(_actor.shutdown(self) for _actor in self.actors.values())
        )
        LOGGER.info("Shutting down sensors")
        await asyncio.gather(
            *(_sensor.shutdown(self) for _sensor in self.sensors)
        )

        self.running = False

        LOGGER.info("Closing all other tasks.")
        await self._finish_all_tasks()
        LOGGER.info("Clossing http session.")
        await self.session.close()

    async def _finish_all_tasks(self):
        LOGGER.info("Finishing ")
        tries = 10
        current_try = 0
        # todo: throttle this as it may run forever if a task cannot be closed.

        all_finished = False
        while not all_finished:
            current_try += 1
            if current_try > tries:
                # giving up cancelling gracefully
                break

            all_finished = True
            for _task in self.tasks:
                if _task.done() or _task.cancelled():
                    pass
                    # all_finished = all_finished and True
                else:
                    _task.cancel()
                    all_finished = False

            if not all_finished:
                await asyncio.sleep(1)

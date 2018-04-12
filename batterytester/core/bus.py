import asyncio
import logging
from asyncio import CancelledError
from threading import Thread

import aiohttp
from async_timeout import timeout

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.helpers import FatalTestFailException, \
    TestSetupException
from batterytester.core.helpers.message_data import FatalData, TestFinished

LOGGER = logging.getLogger(__name__)


class Bus:
    def __init__(self, loop=None):
        self.tasks = []
        self.closing_task = []
        self.threaded_tasks = []
        self.test_runner_task = None
        self.callbacks = []
        self.running = True
        self.loop = loop or asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.exit_message = None
        # self.notifier = BaseNotifier()
        # self.message_bus = Messaging(self.loop)

        self._data_handlers = []
        self.actors = {}
        self.sensors = []

        self.subscriptions = {}

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
    # except KeyError:
    #     LOGGER.debug('No subscribers to subject {}.'.format(subject))

    def subscribe(self, subject, method):
        self.subscriptions[subject] = method

    def task_finished_callback(self, future):
        try:
            val = future.result()
            if val:
                print(val)
        except Exception as err:
            # todo: During cancellation this task can be run multiple times.
            # This needs to be prevented.
            LOGGER.error(err)
            self.notify(subj.TEST_FATAL, FatalData(err))
            """An exception is raised. Meaning one of the long running 
            tasks has encountered an error. Cancelling the main task and
            subsequently cancelling all other long running tasks."""
            if self.test_runner_task:
                self.test_runner_task.cancel()

    def add_async_task(self, coro):
        """Add an async task. The callback will be used to check
        whether these tasks do not exit prematurely. If so, the complete
        test will be stopped."""
        _task = self.loop.create_task(coro)
        _task.add_done_callback(self.task_finished_callback)
        self.tasks.append(_task)

    def add_closing_task(self, coro):
        """Adds all coroutines to a list for later scheduling"""
        self.closing_task.append(coro)

    def add_threaded_task(self, threaded_task: Thread):
        self.threaded_tasks.append(threaded_task)

    def add_callback(self, callback):
        self.callbacks.append(callback)

    async def start_main_test(self, test_runner, test_name):
        await asyncio.gather(
            *(_handler.setup(test_name, self) for _handler in
              self._data_handlers))
        await asyncio.gather(
            *(_actor.setup(test_name, self) for _actor in self.actors.values())
        )
        await asyncio.gather(
            *(_sensor.setup(test_name, self) for _sensor in self.sensors)
        )
        self.test_runner_task = asyncio.ensure_future(test_runner)

        await self.test_runner_task



    def _start_test(self, test_runner, test_name):
        for callback in self.callbacks:
            callback()
        for task in self.threaded_tasks:
            task.start()
        try:
            self.loop.run_until_complete(
                self.start_main_test(test_runner, test_name))
        except TestSetupException as err:
            LOGGER.error(err)
            # sys.exit(1)
        except CancelledError:
            LOGGER.error("Main test loop cancelled.")
        except FatalTestFailException as err:
            LOGGER.error("FATAL ERROR: {}".format(err))
            self.notify(subj.TEST_FATAL, FatalData(err))
        except KeyboardInterrupt:
            LOGGER.info("Test stopped due to keyboard interrupt.")
        except Exception as err:
            LOGGER.error(err)
            self.notify(subj.TEST_FATAL, FatalData(err))
        finally:

            self.loop.run_until_complete(self.stop_test())
            # todo: double check whether all tasks finished
            # checking all_tasks like below.
            # all_tasks = asyncio.Task.all_tasks(self.loop)
            # self.loop.close()

        return self.exit_message

    async def stop_test(self, message=None):

        LOGGER.info("stopping test")

        if self.test_runner_task:
            self.test_runner_task.cancel()

        await asyncio.gather(
            *(_actor.shutdown(self) for _actor in self.actors.values())
        )

        self.notify(subj.TEST_FINISHED, TestFinished())
        for _task in self.closing_task:
            try:
                async with timeout(10):
                    await _task
            except TimeoutError:
                LOGGER.error("problem finishing task: %s", _task)
            except Exception as err:
                LOGGER.error(
                    "problem during execution of closing task: {}".format(err))
        for _handlers in self._data_handlers:
            await _handlers.stop_data_handler()
        await self.session.close()

        # todo: throttle this as it may run forever if a task cannot be closed.
        all_finished = False
        while not all_finished:
            all_finished = True
            for _task in self.tasks:
                if _task.done() or _task.cancelled():
                    pass
                    # all_finished = all_finished and True
                else:
                    _task.cancel()
                    all_finished = False
            await asyncio.sleep(1)
        pass

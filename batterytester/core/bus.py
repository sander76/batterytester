import asyncio
from asyncio import CancelledError

import aiohttp
import logging

from async_timeout import timeout
from threading import Thread

from batterytester.core.helpers.helpers import FatalTestFailException
from batterytester.core.helpers.messaging import Messaging
from batterytester.core.helpers.notifier import BaseNotifier, TelegramNotifier

LOGGER = logging.getLogger(__name__)


class Bus:
    def __init__(self):
        self.tasks = []
        self.closing_task = []
        self.threaded_tasks = []
        self.main_test_task = None
        self.callbacks = []
        self.running = True
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.exit_message = None
        self.notifier = BaseNotifier()
        self.message_bus = Messaging(self.loop)
        # Initialize the message bus
        self.loop.run_until_complete(self.message_bus.start())

    def task_finished_callback(self, future):
        try:
            val = future.result()
            print(val)
        except Exception as err:
            # todo: During cancellation this task can be run multiple times. This needs to be prevented.
            LOGGER.error(err)
            """An exception is raised. Meaning one of the long running 
            tasks has encountered an error. Cancelling the main task and
            subsequently cancelling all other long running tasks."""
            self.main_test_task.cancel()

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

    def _start_test(self):
        # start the ws message bus.

        for callback in self.callbacks:
            callback()
        for task in self.threaded_tasks:
            task.start()
        try:
            self.loop.run_until_complete(self.main_test_task)
        except CancelledError:
            LOGGER.error("Main test loop cancelled.")
        except FatalTestFailException as err:
            LOGGER.error(err)
        finally:
            self.loop.run_until_complete(self.stop_test())
            # todo: double check whether all tasks finished checking all_tasks like below.
            # all_tasks = asyncio.Task.all_tasks(self.loop)
            self.loop.close()

        return self.exit_message

    async def stop_test(self, message=None):
        LOGGER.info("stopping test")

        for _task in self.closing_task:
            try:
                async with timeout(10):
                    await _task
            except TimeoutError:
                LOGGER.error("problem finishing task: %s", _task)

        await self.message_bus.stop_message_bus()
        await self.session.close()

        # todo: throttle this as it may run forever if a task cannot be closed.
        all_finished = False
        while not all_finished:
            all_finished = True
            for _task in self.tasks:
                if _task.done() or _task.cancelled():
                    pass
                    #all_finished = all_finished and True
                else:
                    _task.cancel()
                    all_finished = False
            await asyncio.sleep(1)
        pass
        # if self.running:
        #     self.running = False
        #     task = self.loop.create_task(self._stop_test())
        #     task.add_done_callback(self.stop_loop)

    # @asyncio.coroutine
    # def _stop_test(self):
    #     def _all_running_tasks():
    #         return [task for task in asyncio.Task.all_tasks(self.loop) if
    #                 not (task.done() or task.cancelled())]
    #
    #     self.main_test_task.cancel()
    #
    #     yield from self.message_bus.stop_message_bus()
    #     yield from self.session.close()
    #     _all_tasks = _all_running_tasks()
    #     while _all_tasks:
    #         for _task in _all_tasks:
    #             _task.cancel()
    #         yield from asyncio.sleep(1)
    #         _all_tasks = _all_running_tasks()
    #
    #     # todo: manage the threaded tasks too.
    #     # self.threaded_tasks =
    #     #     [task for task in self.threaded_tasks if task.is_alive()]


class TelegramBus(Bus):
    def __init__(self, telegram_token, chat_id, test_name):
        super().__init__()
        self.notifier = TelegramNotifier(self.loop, telegram_token, chat_id,
                                         test_name=test_name)

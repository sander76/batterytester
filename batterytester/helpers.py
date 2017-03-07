import asyncio
from asyncio.futures import CancelledError
from threading import Thread

import aiohttp
import time

LOOP_TIME_OUT = 2


class Bus:
    def __init__(self):
        self.all_tasks = []
        self.tasks = []
        self.threaded_tasks = []
        self.callbacks = []
        self.running = True
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.exit_message = None

    def add_async_task(self, coro):
        self.tasks.append(self.loop.create_task(coro))

    def add_threaded_task(self, threaded_task: Thread):
        self.threaded_tasks.append(threaded_task)

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def add_task(self, task):
        self.all_tasks.append(task)

    def start_test(self):
        for callback in self.callbacks:
            callback()
        for task in self.threaded_tasks:
            task.start()
        try:
            self.loop.run_forever()
        finally:
            self.loop.close()
        return self.exit_message

    def stop_loop(self, future):
        time.sleep(3)
        self.loop.stop()

    def stop_test(self, message=None):
        # todo: log the message to email.
        self.exit_message = message
        # self.running = False
        task = self.loop.create_task(self._stop_test())
        task.add_done_callback(self.stop_loop)

    @asyncio.coroutine
    def _stop_test(self):
        for task in self.tasks:
            try:
                task.cancel()
            except CancelledError as e:
                pass
        for task in self.threaded_tasks:
            task.stop()
        while self.tasks or self.threaded_tasks:
            yield from asyncio.sleep(1)
            self.tasks = [task for task in self.tasks if
                          not (task.done() or task.cancelled())]
            self.threaded_tasks = [task for task in self.threaded_tasks if
                                   task.is_alive()]

        yield from self.session.close()

        # @asyncio.coroutine
        # def _stop_test(self):
        #     while self.tasks or self.threaded_tasks:
        #         self.tasks = [task for task in self.tasks if
        #                       not task.done()]
        #         tasks = [task for task in asyncio.Task.all_tasks(self.loop) if
        #                  not task.done()]
        #         self.threaded_tasks = [task for task in self.threaded_tasks if
        #                                task.is_alive()]
        #
        #         yield from asyncio.sleep(1)
        #     yield from self.session.close()


bus = Bus()


def get_bus() -> Bus:
    return bus

# class Looper:
#     def __init__(self):
#         self.looping = True
#
#     def stop_loop(self):
#         self.looping = False

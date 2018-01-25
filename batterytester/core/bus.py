import asyncio
from threading import Thread

import aiohttp

from batterytester.core.helpers.messaging import Messaging
from batterytester.core.helpers.notifier import BaseNotifier, TelegramNotifier


class Bus:
    def __init__(self):
        self.tasks = []
        self.threaded_tasks = []
        self.callbacks = []
        self.running = True
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.exit_message = None
        self.notifier = BaseNotifier()
        self.message_bus = Messaging(self.loop)
        self.loop.run_until_complete(self.message_bus.start())

    def add_async_task(self, coro):
        self.tasks.append(self.loop.create_task(coro))

    def add_threaded_task(self, threaded_task: Thread):
        self.threaded_tasks.append(threaded_task)

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def _start_test(self):
        #start the ws message bus.

        for callback in self.callbacks:
            callback()
        for task in self.threaded_tasks:
            task.start()
        try:
            self.loop.run_forever()
        finally:
            #all_tasks = asyncio.Task.all_tasks(self.loop)
            self.loop.close()

        return self.exit_message


    def stop_loop(self, future):
        self.loop.stop()

    def stop_test(self, message=None):
        if self.running:
            self.running = False
            task = self.loop.create_task(self._stop_test())
            task.add_done_callback(self.stop_loop)

    @asyncio.coroutine
    def _stop_test(self):
        _all_tasks = [_task for _task in asyncio.Task.all_tasks(self.loop) if
                      not asyncio.Task.current_task(self.loop) == _task]
        print("session:")
        print(self.session)
        yield from self.message_bus.stop_message_bus()
        yield from self.session.close()
        # if self.session.closed:
        #     break
        yield from asyncio.sleep(2)

        for _task in _all_tasks:
            _task.cancel()
        while _all_tasks or self.threaded_tasks:
            yield from asyncio.sleep(1)
            _all_tasks = [task for task in _all_tasks if
                          not (task.done() or task.cancelled())]
            self.threaded_tasks = [task for task in self.threaded_tasks if
                                   task.is_alive()]


class TelegramBus(Bus):
    def __init__(self, telegram_token, chat_id, test_name):
        super().__init__()
        self.notifier = TelegramNotifier(self.loop, telegram_token, chat_id,
                                         test_name=test_name)

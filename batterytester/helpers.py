import asyncio
import os
from asyncio.futures import CancelledError
from asyncio import AbstractServer

from threading import Thread

import aiohttp
import time

import logging

import datetime

LOOP_TIME_OUT = 2

_LOGGER = logging.getLogger(__name__)


def get_current_time():
    return datetime.datetime.now().replace(microsecond=0)


# def slugify(text: str) -> str:
#     """Slugify a given text."""
#     text = normalize('NFKD', text)
#     text = text.lower()
#     text = text.replace(" ", "_")
#     text = text.translate(TBL_SLUGIFY)
#     text = RE_SLUGIFY.sub("", text)
#
#     return text

# todo: move this to the general library.
class TestFailException(Exception):
    pass


def check_output_location(test_location):
    if os.path.exists(test_location):
        files = os.listdir(test_location)
        if files:
            print("TEST LOCATION ALLREADY CONTAINS FILES")
            print("IF PROCEED ALL CONTAINING DATA WILL BE ERASED.")
            proceed = input("PROCEED ? [y/n] >")
            if proceed == 'y':
                # clear all files in folder.
                for _fl in files:
                    os.remove(os.path.join(test_location,_fl))
                return True
            else:
                return False
    if not os.path.exists(test_location):
        os.makedirs(test_location)
    return True


class Bus:
    def __init__(self):
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

    def start_test(self):
        for callback in self.callbacks:
            callback()
        for task in self.threaded_tasks:
            task.start()
        try:
            self.loop.run_forever()
        finally:
            all_tasks = asyncio.Task.all_tasks(self.loop)
            self.loop.close()

        return self.exit_message

    def stop_loop(self, future):
        self.loop.stop()

    def stop_test(self, message=None):
        self.running = False
        task = self.loop.create_task(self._stop_test())
        task.add_done_callback(self.stop_loop)

    @asyncio.coroutine
    def _stop_test(self):
        _all_tasks = [_task for _task in asyncio.Task.all_tasks(self.loop) if
                      not asyncio.Task.current_task(self.loop) == _task]
        print("session:")
        print(self.session)
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

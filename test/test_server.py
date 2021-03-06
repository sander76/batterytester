import asyncio
import logging
import os

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.message_data import TestWarmup

logging.basicConfig(level=logging.DEBUG)
from batterytester.server.server import Server, get_loop


def get_full_path(file):
    this_folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(this_folder, file)


# todo: create a fake websocket tester connection and test interaction.

def test_process():
    """Test a process raising an unhandled exception."""
    loop = get_loop()
    server = Server()
    _file = get_full_path('fake_process_one.py')

    async def start_process():
        await server._start_test_process(_file)
        while not server.process_task.done():
            await asyncio.sleep(1)
        return

    loop.run_until_complete(start_process())
    assert server.test_is_running is False


def test_stop_process_no_ws():
    loop = get_loop()
    server = Server(loop_=loop)
    _file = get_full_path('fake_process_two.py')

    async def start_process():
        await server._start_test_process(_file)
        assert server.test_is_running is True
        await asyncio.sleep(1)
        resp = await server.stop_test()
        while not server.process_task.done():
            await asyncio.sleep(1)
        return

    loop.run_until_complete(start_process())
    assert server.test_is_running is False


def test__update_test_cache():
    server = Server()
    data = TestWarmup('name', 10)
    _js = data.to_dict()
    server._update_test_cache(_js, subj.TEST_WARMUP)
    assert server.test_cache[subj.TEST_WARMUP] == _js


def test_server_start_stop():
    loop = get_loop()
    server = Server(config_folder='', loop_=loop)

    async def start():
        await server.start()

    async def stop():
        await server.stop_data_handler()

    async def test():
        await start()
        await asyncio.sleep(1)
        await stop()

    loop.run_until_complete(test())

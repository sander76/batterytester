"""Websocket server for inter process communication"""

import asyncio
import json
import logging
import sys
from argparse import ArgumentParser
from pathlib import Path

import aiohttp
import async_timeout
from aiohttp import web, WSCloseCode

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.constants import KEY_SUBJECT
from batterytester.core.helpers.message_data import to_serializable, \
    Data, ProcessData, STATUS_FINISHED, STATUS_RUNNING, STATUS_STARTING
from batterytester.core.helpers.message_subjects import PROCESS_STARTED, \
    PROCESS_INFO
from batterytester.server.logger import setup_logging

ATTR_MESSAGE_BUS_ADDRESS = '0.0.0.0'
ATTR_MESSAGE_BUS_PORT = 8567

URL_CLOSE = 'close'
MSG_TYPE_ATOM = 'atom'  # General info about the current atom.
MSG_TYPE_TEST = 'test'  # General test information.
MSG_TYPE_STOP_TEST = 'stop_test'
MSG_TYPE_ALL_TESTS = 'all_tests'

CACHE_TEST_DATA = 'test_data'  # Cache key where to store test info.

LOGGER = logging.getLogger(__name__)

KEY_PASS = 'passed'
KEY_FAIL = 'failed'
ATTR_FAILED_IDS = 'failed_ids'

URL_INTERFACE = '/ws'
URL_TEST = '/ws/tester'
URL_TEST_STOP = '/test_stop'
URL_TEST_START = '/test_start'
URL_ALL_TESTS = '/all_tests'

DEFAULT_CONFIG_PATH = '/home/pi/test_configs'


class Server:
    def __init__(self, config_folder=None, loop_=None):
        self.client_sockets = []  # connected ui clients
        self.test_ws = None  # Socket connection to the actual running test.
        self.config_folder = config_folder
        self.loop = loop_ or asyncio.get_event_loop()
        self.app = web.Application(loop=self.loop)
        self.runner = None
        self.server = None
        self.test_cache = {}
        self.test_process = None
        self.process_data = ProcessData()

    @property
    def test_is_running(self):
        if self.test_process is None:
            return False
        return True

    def _add_routes(self):
        # User interface(s) connects here.
        self.app.router.add_get(URL_INTERFACE, self.client_handler)
        # Test connects here.
        self.app.router.add_get(URL_TEST, self.test_handler)
        self.app.router.add_static('/static/', path='static', name='static')
        self.app.router.add_post(URL_TEST_START, self.test_start_handler)
        self.app.router.add_post(URL_TEST_STOP, self.stop_test_handler)
        self.app.router.add_get('/get_status', self.get_status_handler)

    def start_server(self):
        """Create a web server"""
        try:
            self.loop.run_until_complete(self.start())
        except Exception as err:
            LOGGER.error(err)

    def list_configs(self):
        data = {"data": [], KEY_SUBJECT: MSG_TYPE_ALL_TESTS}
        if self.config_folder:
            p = Path(self.config_folder)
            data['data'] = [pth.name for pth in
                            p.glob('*.py')]
        return data

    async def test_start_handler(self, request):
        data = await request.json()
        p = str(Path(self.config_folder).joinpath(data['test']))

        if self.test_is_running:
            return web.Response(
                text="There is another test running. Stop that one first.")
        else:
            await self._start_test_process(p)

            self.process_data.process_name = data['test']
            await self.send_to_client(self.process_data.to_json())
        return web.Response()

        # todo: handle feedback over websocket.

    async def _start_test_process(self, p):
        self.clear_cache()
        self.process_data.status = STATUS_STARTING
        self.process_data.subj = PROCESS_STARTED
        await self.send_to_client(self.process_data.to_json())

        self.test_process = await asyncio.create_subprocess_exec(
            sys.executable, p,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT, loop=self.loop
        )
        self.process_data.status = STATUS_RUNNING
        self.process_data.subj = PROCESS_INFO
        self.process_data.process_id = self.test_process.pid

        self.process_task = asyncio.ensure_future(self.manage_process())

    async def manage_process(self):
        try:
            while not self.test_process.stdout.at_eof():
                line = await self.test_process.stdout.readline()
                self.process_data.add_message(line.decode('utf-8'))
                await self.send_to_client(self.process_data.to_json())
            # log, other = await self.test_process.communicate()
            code = await self.test_process.wait()

            # unicode_log = log.decode('utf-8')
            LOGGER.debug('exit code: {}'.format(code))
            # LOGGER.debug(unicode_log)

            self.process_data.return_code = code
            # self.process_data.add_message(unicode_log)
            self.process_data.status = STATUS_FINISHED
            await self.send_to_client(
                self.process_data.to_json()
            )

        except Exception as err:
            LOGGER.exception(err)
            await self.stop_test()
        finally:
            self.test_process = None

    async def stop_test_handler(self, request):
        # todo: if no websocket connection somehow. Just kill the process.
        await self.stop_test()
        # data = await request.text()
        # resp = await self.send_to_tester(data)
        return web.json_response({"running": False})

    async def get_status_handler(self, request):
        self.test_cache['process_info'] = self.process_data.to_dict()
        return web.json_response(self.test_cache)

    async def stop_test(self):
        """Stop the running test process."""
        if self.test_is_running:
            if self.test_ws is not None:
                try:
                    with async_timeout.timeout(5):
                        await self.test_ws.send_str(
                            json.dumps({'type': MSG_TYPE_STOP_TEST}))
                except asyncio.TimeoutError:
                    LOGGER.warning("Graceful shutdown failed.")
                    self.close_tester_connection()
                    await self.stop_test()
            else:
                LOGGER.warning("killing the process.")

                self.test_process.kill()

    async def close_tester_connection(self):
        if self.test_ws is not None:
            try:
                with async_timeout.timeout(5):
                    await self.test_ws.close()
            except asyncio.TimeoutError:
                LOGGER.warning(
                    "unable to close the tester websocket connection"
                    "gracefully")
            finally:
                self.test_ws = None
        _data = self.test_cache.get(subj.TEST_WARMUP)
        if _data:
            _data['status'] = Data('tester disconnected')
            await self.send_to_client(
                json.dumps(_data, default=to_serializable))

    async def test_handler(self, request):
        """Handle incoming data from the running test."""
        self.test_ws = web.WebSocketResponse()
        await self.test_ws.prepare(request)
        try:
            async for msg in self.test_ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    LOGGER.debug(msg.data)
                    _data = json.loads(msg.data)
                    await self._parse_incoming_test_data(_data, msg.data)
                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await self.close_tester_connection()
        except Exception as err:
            LOGGER.error(err)
            await self.close_tester_connection()

        return self.test_ws

    async def client_handler(self, request):
        """Handle connection to the connected user interfaces."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.client_sockets.append(ws)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:

                    _data = json.loads(msg.data)
                    _type = _data['type']
                    if _type == URL_CLOSE:
                        await ws.close()
                    elif _type == MSG_TYPE_ALL_TESTS:
                        await self.send_to_client(
                            json.dumps(self.list_configs()))

                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await ws.close()
        finally:
            self.client_sockets.remove(ws)
        return ws

    async def _parse_incoming_test_data(self, data, raw):
        await self.send_to_client(raw)

        try:
            _subj = data[KEY_SUBJECT]

        except KeyError:
            LOGGER.error('{} has no subj defined.')
        else:
            if (_subj == subj.TEST_FINISHED or
                    _subj == subj.TEST_FATAL or
                    _subj == subj.TEST_WARMUP or
                    _subj == subj.TEST_RESULT):

                self._update_test_cache(data, subj.TEST_WARMUP)
            elif (_subj == subj.ATOM_WARMUP or
                  _subj == subj.ATOM_STATUS or
                  _subj == subj.ATOM_RESULT or
                  _subj == subj.ATOM_FINISHED):

                self._update_test_cache(data, subj.ATOM_WARMUP)
            elif _subj == subj.SENSOR_DATA:
                self._update_test_cache(data, subj.SENSOR_DATA)

    def _update_test_cache(self, data, cache_key):
        if cache_key not in self.test_cache:
            self.test_cache[cache_key] = {}
        for key, value in data.items():
            self.test_cache[cache_key][key] = value

    def clear_cache(self):
        self.test_cache = {}
        self.process_data = ProcessData()

    async def send_to_client(self, raw):
        res = await asyncio.gather(
            *(_ws.send_str(raw) for _ws in self.client_sockets))
        for _res in res:
            LOGGER.debug(_res)

    async def shutdown(self):
        for ws in self.client_sockets:
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='server shutdown')

    async def start(self):
        """Initialize this data handler"""
        self._add_routes()
        # self.handler = self.app.make_handler()
        self.runner = web.AppRunner(self.app)

        await self.runner.setup()
        self.server = web.TCPSite(
            self.runner,
            host=ATTR_MESSAGE_BUS_ADDRESS,
            port=ATTR_MESSAGE_BUS_PORT)
        await self.server.start()

    async def stop_data_handler(self):
        # self.server.close()
        # await self.server.wait_closed()
        await self.shutdown()
        await self.runner.cleanup()
        # await self.handler.shutdown(60.0)
        # await self.app.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument('--config_path',
                        help="path where config files are located.",
                        default=DEFAULT_CONFIG_PATH)
    parser.add_argument('--log_folder',
                        help="log file location",
                        )

    args = parser.parse_args()
    _config_folder = args.config_path
    _log_folder = args.log_folder

    setup_logging(LOGGER, _log_folder)

    if sys.platform == 'win32':
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    server = Server(
        config_folder=_config_folder,
        loop_=loop)
    server.start_server()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(server.stop_data_handler())
    loop.close()

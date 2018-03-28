"""Websocket server for inter process communication"""

import asyncio
import json
import logging
from pathlib import Path

import aiohttp
from aiohttp import web, WSCloseCode

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.constants import KEY_SUBJECT, KEY_CACHE
from batterytester.core.helpers.message_data import to_serializable, \
    Data

ATTR_MESSAGE_BUS_ADDRESS = '0.0.0.0'
ATTR_MESSAGE_BUS_PORT = 8567

URL_CLOSE = 'close'
MSG_TYPE_ATOM = 'atom'  # General info about the current atom.
MSG_TYPE_TEST = 'test'  # General test information.
MSG_TYPE_STOP_TEST = 'stop_test'
MSG_TYPE_ALL_TESTS = 'all_tests'

CACHE_ATOM_DATA = 'atom_data'  # Cache key where to store atom data.
CACHE_TEST_DATA = 'test_data'  # Cache key where to store test info.

LOGGER = logging.getLogger(__name__)

KEY_PASS = 'passed'
KEY_FAIL = 'failed'
ATTR_FAILED_IDS = 'failed_ids'

URL_INTERFACE = '/ws'
URL_TEST = '/ws/tester'
URL_TEST_STOP = '/test_stop'
URL_TEST_START = '/test_start'


class Server:
    def __init__(self, config_folder=None, loop_=None):
        self.sensor_sockets = []  # connected ui clients
        self.test_ws = None  # Socket connection to the actual running test.
        self.config_folder = config_folder
        self.loop = loop_ or asyncio.get_event_loop()
        self.app = web.Application()
        self._add_routes()
        self.handler = None
        self.server = None
        self.test_cache = {}
        # self.test_summary = TestSummary()

    def _add_routes(self):
        # User interface connects here.
        self.app.router.add_get(URL_INTERFACE, self.sensor_handler)
        # tests connect here
        self.app.router.add_get(URL_TEST, self.test_handler)
        self.app.router.add_static('/static/', path='static', name='static')
        self.app.router.add_post(URL_TEST_START, self.test_start_handler)
        self.app.router.add_post(URL_TEST_STOP, self.test_stop_handler)

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
        pass

    async def test_stop_handler(self, request):
        data = await request.json()
        resp = self.send_to_tester(data)
        return web.json_response({"running": resp})

    async def test_handler(self, request):
        """Handle incoming data from the running test."""
        self.test_ws = web.WebSocketResponse()
        await self.test_ws.prepare(request)
        try:
            async for msg in self.test_ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    LOGGER.debug(msg.data)
                    _data = json.loads(msg.data)
                    self._parse_incoming(_data, msg.data)
                else:
                    await self.test_ws.close()
        except Exception as err:
            LOGGER.error(err)
            self._tester_disconnect()

        return self.test_ws

    async def sensor_handler(self, request):
        """Handle connection to the connected user interfaces."""
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.sensor_sockets.append(ws)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:

                    _data = json.loads(msg.data)
                    _type = _data['type']
                    if _type == URL_CLOSE:
                        await ws.close()
                    elif _type == MSG_TYPE_ATOM:
                        self.return_cached_data(
                            ws, subj.ATOM_WARMUP)
                        self.return_cached_data(
                            ws, subj.ATOM_STATUS
                        )
                    elif _type == MSG_TYPE_TEST:
                        self.return_cached_data(
                            ws, subj.TEST_WARMUP)
                        self.return_cached_data(
                            ws, subj.RESULT_SUMMARY
                        )

                    elif _type == MSG_TYPE_ALL_TESTS:
                        self._send_json_to_clients(self.list_configs())

                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await ws.close()
        finally:
            self.sensor_sockets.remove(ws)
        return ws

    def send_to_tester(self, data: str):
        if self.test_ws:
            asyncio.ensure_future(self.test_ws.send_str(data))
            return True
        return False

    def _parse_incoming(self, data, raw):
        self._send_to_ws(data, raw)
        if data[KEY_SUBJECT] == subj.TEST_WARMUP:
            self.test_cache = {}
        if data.get(KEY_CACHE):
            self.test_cache[data[KEY_SUBJECT]] = data

    def _tester_disconnect(self):
        _data = self.test_cache.get(subj.TEST_WARMUP)
        if _data:
            _data['status'] = Data('tester disconnected')
            self._send_to_ws(_data, json.dumps(_data, default=to_serializable))

    def _send_json_to_clients(self, js):
        for _ws in self.sensor_sockets:
            asyncio.ensure_future(_ws.send_json(js))

    def _send_to_ws(self, data, raw):
        for _ws in self.sensor_sockets:
            asyncio.ensure_future(_ws.send_str(raw))

    def return_cached_data(self, ws_client, cache_key):
        cached_data = self.test_cache.get(cache_key)
        if cached_data:
            _js = json.dumps(cached_data, default=to_serializable)
            asyncio.ensure_future(ws_client.send_str(_js))

    async def shutdown(self):
        for ws in self.sensor_sockets:
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='server shutdown')

    async def start(self):
        self.handler = self.app.make_handler()
        self.server = await self.loop.create_server(
            self.handler, ATTR_MESSAGE_BUS_ADDRESS, ATTR_MESSAGE_BUS_PORT)

    async def stop_data_handler(self):
        self.server.close()
        await self.server.wait_closed()
        await self.shutdown()
        await self.handler.shutdown(60.0)
        await self.app.cleanup()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    server = Server(
        config_folder='C:\\Users\\sander\\Hunter Douglas Europe B.V\\Motorisation Projects Site - Documents\\Test Setup\\test_configs',
        loop_=loop)
    server.start_server()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(server.stop_data_handler())
    loop.close()

"""Websocket server for inter process communication"""

import json
import aiohttp
import logging

import batterytester.core.helpers.message_subjects as subj

from aiohttp import web

from batterytester.core.datahandlers import BaseDataHandler

ATTR_MESSAGE_BUS_ADDRESS = '0.0.0.0'
ATTR_MESSAGE_BUS_PORT = 8567

URL_CLOSE = 'close'
URL_ATOM = 'atom'  # General info about the current atom.
URL_TEST = 'test'  # General test information.

CACHE_ATOM_DATA = 'atom_data'  # Cache key where to store atom data.
CACHE_TEST_DATA = 'test_data'  # Cache key where to store test info.

LOGGER = logging.getLogger(__name__)


# todo: move the websocket server to a separate process and connect to it with a client connection.

class Messaging(BaseDataHandler):
    def __init__(self, loop):
        self.sensor_sockets = []
        self.report_sockets = []
        self.loop = loop
        self.app = web.Application()
        self.app.router.add_get('/ws', self.sensor_handler)
        self.handler = None
        self.server = None
        self._report = None
        self.test_cache = {}
        try:
            self.loop.run_until_complete(self.start())
        except Exception as err:
            LOGGER.error(err)

    def get_subscriptions(self):
        return (
            (subj.TEST_START, self.test_data),
            (subj.TEST_WARMUP, self.test_data_cached),
            (subj.ATOM_EXECUTING, self.atom_status_cached),
            (subj.ATOM_WARMUP, self.test_data_cached),
            (subj.SENSOR_DATA, self.test_data)
        )

    def test_data(self, subject, data, *args, **kwargs):
        data[subj.SUBJ] = subject
        self._send_to_ws(data)

    def test_data_cached(self, subject, data):
        data[subj.SUBJ] = subject
        self.test_cache[subject] = data
        self._send_to_ws(data)

    def atom_status_cached(self, subject, data):
        data[subj.SUBJ] = subject
        self.test_cache[subject] = data
        self._send_to_ws(data)

    async def sensor_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.sensor_sockets.append(ws)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == URL_CLOSE:
                        await ws.close()
                    elif msg.data == URL_ATOM:
                        self.return_cached_data(
                            ws, subj.ATOM_WARMUP)
                    elif msg.data == URL_TEST:
                        self.return_cached_data(
                            ws, subj.TEST_WARMUP)
                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await ws.close()
        finally:
            self.sensor_sockets.remove(ws)
        return ws

    def return_cached_data(self, ws_client, cache_key):
        cached_data = self.test_cache.get(cache_key)
        if cached_data:
            _js = json.dumps(cached_data)
            ws_client.send_str(_js)

    # def send_data(self, data: dict):
    #     self._send_to_ws(data)
    #
    # def send_data_cached(self, data: dict, cache_key: str):
    #     if data:
    #         data['type'] = cache_key
    #         self.test_cache[cache_key] = data
    #         self._send_to_ws(data)
    #
    # def send_atom_data(self, data):
    #     if data:
    #         data['type'] = CACHE_ATOM_DATA
    #         self._send_to_ws(data)

    def _send_to_ws(self, data: dict):
        _js = json.dumps(data)
        for _ws in self.sensor_sockets:
            _ws.send_str(_js)

    async def start(self):
        self.handler = self.app.make_handler()
        self.server = await self.loop.create_server(
            self.handler, ATTR_MESSAGE_BUS_ADDRESS, ATTR_MESSAGE_BUS_PORT)

    async def stop_data_handler(self):
        self.server.close()
        await self.server.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown(60.0)
        await self.app.cleanup()

"""Websocket server for inter process communication"""

import json
import aiohttp

from aiohttp import web

ATTR_MESSAGE_BUS_ADDRESS = '0.0.0.0'
ATTR_MESSAGE_BUS_PORT = 8567

URL_CLOSE = 'close'
URL_ATOM = 'atom'  # General info about the current atom.
URL_TEST = 'test'  # General test information.

CACHE_ATOM_DATA = 'atom_data'  # Cache key where to store atom data.
CACHE_TEST_DATA = 'test_data'  # Cache key where to store test info.


# todo: move the websocket server to a separate process and connect to it with a client connection. Another option would be to use mqtt for easier pub sub actions.

class Messaging:
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
                        ws.send_str(self.test_cache[CACHE_ATOM_DATA])
                    elif msg.data == URL_TEST:
                        ws.send_str(self.test_cache[CACHE_TEST_DATA])
                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await ws.close()
        finally:
            self.sensor_sockets.remove(ws)
        return ws

    def send_data(self, data: dict):
        _js = json.dumps(data)
        self._send_to_ws(_js)

    def send_data_cached(self, data: dict, cache_key: str):
        data['type'] = cache_key
        _js = json.dumps(data)

        self.test_cache[cache_key] = _js
        self._send_to_ws(_js)

    def _send_to_ws(self, data: str):
        for _ws in self.sensor_sockets:
            _ws.send_str(data)

    async def start(self):
        self.handler = self.app.make_handler()
        self.server = await self.loop.create_server(
            self.handler, ATTR_MESSAGE_BUS_ADDRESS, ATTR_MESSAGE_BUS_PORT)

    async def stop_message_bus(self):
        self.server.close()
        await self.server.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown(60.0)
        await self.app.cleanup()

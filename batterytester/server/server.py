"""Websocket server for inter process communication"""

import asyncio
import json
import logging

import aiohttp
from aiohttp import web, WSCloseCode

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.constants import KEY_SUBJECT, KEY_CACHE
from batterytester.core.helpers.message_data import to_serializable, \
    Data

ATTR_MESSAGE_BUS_ADDRESS = '0.0.0.0'
ATTR_MESSAGE_BUS_PORT = 8567

URL_CLOSE = 'close'
URL_ATOM = 'atom'  # General info about the current atom.
URL_TEST = 'test'  # General test information.

CACHE_ATOM_DATA = 'atom_data'  # Cache key where to store atom data.
CACHE_TEST_DATA = 'test_data'  # Cache key where to store test info.

LOGGER = logging.getLogger(__name__)

KEY_PASS = 'passed'
KEY_FAIL = 'failed'
ATTR_FAILED_IDS = 'failed_ids'


class Server:
    def __init__(self, loop_):
        self.sensor_sockets = []
        self.loop = loop_
        self.app = web.Application()
        self.app.router.add_get('/ws', self.sensor_handler)
        self.app.router.add_get('/ws/tester', self.test_handler)
        self.app.router.add_static('/static/', path='static', name='static')

        self.handler = None
        self.server = None
        self.test_cache = {}
        # self.test_summary = TestSummary()
        try:
            self.loop.run_until_complete(self.start())
        except Exception as err:
            LOGGER.error(err)

    async def test_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    LOGGER.debug(msg.data)
                    _data = json.loads(msg.data)
                    self._parse_incoming(_data, msg.data)
                else:
                    await ws.close()
        except Exception as err:
            LOGGER.error(err)
            self._tester_disconnect()

        return ws

    async def sensor_handler(self, request):
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
                    elif _type == URL_ATOM:
                        self.return_cached_data(
                            ws, subj.ATOM_WARMUP)
                        self.return_cached_data(
                            ws, subj.ATOM_STATUS
                        )
                    elif _type == URL_TEST:
                        self.return_cached_data(
                            ws, subj.TEST_WARMUP)
                        self.return_cached_data(
                            ws, subj.RESULT_SUMMARY
                        )

                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await ws.close()
        finally:
            self.sensor_sockets.remove(ws)
        return ws

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

    def _send_to_ws(self, data, raw):
        for _ws in self.sensor_sockets:
            _ws.send_str(raw)

    def return_cached_data(self, ws_client, cache_key):
        cached_data = self.test_cache.get(cache_key)
        if cached_data:
            _js = json.dumps(cached_data, default=to_serializable)
            ws_client.send_str(_js)

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
    server = Server(loop)
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(server.stop_data_handler())
    loop.close()

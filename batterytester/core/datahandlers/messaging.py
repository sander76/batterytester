"""Websocket server for inter process communication"""

import json
import aiohttp
import logging

import batterytester.core.helpers.message_subjects as subj

from aiohttp import web

from batterytester.core.datahandlers import BaseDataHandler
from batterytester.core.helpers.message_data import to_serializable, FatalData, \
    TestFinished, TestData, AtomData, AtomStatus, AtomResult, TestSummary
from batterytester.core.helpers.constants import KEY_ATOM_LOOP, KEY_VALUE, \
    KEY_ATOM_INDEX, ATTR_RESULT, KEY_ATOM_NAME, REASON

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


# todo: move the websocket server to a separate process and connect to it with a client connection.

class Messaging(BaseDataHandler):
    def __init__(self, loop):
        super().__init__()
        self.sensor_sockets = []
        self.report_sockets = []
        self.loop = loop
        self.app = web.Application()
        self.app.router.add_get('/ws', self.sensor_handler)
        self.handler = None
        self.server = None
        self._report = None
        self.test_cache = {}
        self.test_summary = TestSummary()
        try:
            self.loop.run_until_complete(self.start())
        except Exception as err:
            LOGGER.error(err)

    def get_subscriptions(self):
        return (
            (subj.TEST_WARMUP, self.test_warmup),
            (subj.TEST_FATAL, self.test_fatal),
            (subj.TEST_FINISHED, self.test_finished),
            (subj.ATOM_STATUS, self.atom_status),
            (subj.ATOM_WARMUP, self._atom_warmup),
            (subj.ATOM_RESULT, self.atom_result),
            (subj.SENSOR_DATA, self.test_data)
        )

    def _atom_warmup(self, subject, data: AtomData):
        super()._atom_warmup(subject, data)
        data.subj = subject
        self.test_cache[subject] = data
        self._send_to_ws(data)

    def test_warmup(self, subject, data: TestData):
        LOGGER.debug("warmup test: {} data: {}".format(subject, data))
        data.subj = subject
        self.test_cache[subject] = data
        self._send_to_ws(data)

    def test_fatal(self, subject, data: FatalData):
        data.subj = subject
        self._send_to_ws(data)

    def test_finished(self, subject, data: TestFinished):
        data.subj = subject
        self._send_to_ws(data)

    def atom_result(self, subject, data: AtomResult):
        """Sends out a summary of the current running test result."""
        if data.passed.value:
            self.test_summary.atom_passed()
        else:
            self.test_summary.atom_failed(
                self._current_idx,
                self._current_loop,
                self._atom_name,
                data.reason.value)

        self.test_data(subject, dict(vars(self.test_summary)))
        self.test_summary.subj = subject
        self._send_to_ws(self.test_summary)

    def test_data(self, subject, data, *args, **kwargs):
        data[subj.SUBJ] = subject
        self._send_to_ws(data)

    # def test_data_cached(self, subject, data):
    #     data[subj.SUBJ] = subject
    #     self.test_cache[subject] = data
    #     self._send_to_ws(data)

    def atom_status(self, subject, data: AtomStatus):
        data.subj = subject
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
                        self.return_cached_data(
                            ws, subj.ATOM_STATUS
                        )
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
            _js = json.dumps(cached_data, default=to_serializable)
            ws_client.send_str(_js)

    def _send_to_ws(self, data: dict):
        _js = json.dumps(data, default=to_serializable)
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

"""Websocket server for inter process communication"""

import asyncio
import json
import logging
from json import JSONDecodeError

import aiohttp

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.datahandlers import BaseDataHandler
from batterytester.core.helpers.helpers import FatalTestFailException
from batterytester.core.helpers.message_data import to_serializable, \
    FatalData, TestFinished, TestData, AtomData, \
    AtomStatus, AtomResult, TestSummary, Message, LoopData
from batterytester.server.server import URL_TEST, MSG_TYPE_STOP_TEST

ATTR_MESSAGE_BUS_ADDRESS = '127.0.0.1'
ATTR_MESSAGE_BUS_PORT = 8567

URL_CLOSE = 'close'
URL_ATOM = 'atom'  # General info about the current atom.
# URL_TEST = 'test'  # General test information.

CACHE_ATOM_DATA = 'atom_data'  # Cache key where to store atom data.
CACHE_TEST_DATA = 'test_data'  # Cache key where to store test info.

LOGGER = logging.getLogger(__name__)

KEY_PASS = 'passed'
KEY_FAIL = 'failed'
ATTR_FAILED_IDS = 'failed_ids'


class Messaging(BaseDataHandler):
    def __init__(self):
        super().__init__()
        self.ws_connection = None
        self.session = None
        self.test_summary = TestSummary()
        self.test_summary.cache = True
        # self._bus.add_async_task(self.ws_connect())

    def get_subscriptions(self):
        return (
            (subj.TEST_WARMUP, self.test_warmup),
            (subj.TEST_FATAL, self.test_fatal),
            (subj.TEST_FINISHED, self.test_finished),
            (subj.ATOM_STATUS, self.atom_status),
            (subj.LOOP_WARMUP, self.loop_warmup),
            (subj.ATOM_WARMUP, self._atom_warmup),
            (subj.ATOM_RESULT, self.atom_result),
            (subj.SENSOR_DATA, self.test_data)
        )

    async def stop_data_handler(self):
        await self.ws_connection.close()

    def loop_warmup(self, subject, data: LoopData):
        data.subj = subject
        self._send_to_ws(data)

    def _atom_warmup(self, subject, data: AtomData):
        super()._atom_warmup(subject, data)
        data.subj = subject
        data.cache = True
        self._send_to_ws(data)

    def test_warmup(self, subject, data: TestData):
        LOGGER.debug("warmup test: {} data: {}".format(subject, data))
        data.subj = subject
        data.cache = True
        self._send_to_ws(data)

    def test_fatal(self, subject, data: FatalData):
        data.subj = subject
        self._send_to_ws(data)

    def test_finished(self, subject, data: TestFinished):
        data.subj = subject
        self._send_to_ws(data)

    def atom_result(self, subject, data: AtomResult):
        """Sends out a summary of the current running test result."""
        data.cache = True
        if data.passed.value:
            self.test_summary.atom_passed()
        else:
            self.test_summary.atom_failed(
                self._current_idx,
                self._current_loop,
                self._atom_name,
                data.reason.value)

        # self.test_data(subject, dict(vars(self.test_summary)))
        # self.test_summary.subj = subject
        self._send_to_ws(self.test_summary)

    def test_data(self, subject, data):
        self._send_to_ws(data)

    def atom_status(self, subject, data: AtomStatus):
        data.subj = subject
        data.cache = True
        self._send_to_ws(data)

    def _send_to_ws(self, data: Message):
        _js = json.dumps(data, default=to_serializable)
        asyncio.ensure_future(self.ws_connection.send_str(_js))

    async def setup(self, test_name, bus):
        self._bus = bus
        try:
            self.ws_connection = await asyncio.wait_for(
                self._bus.session.ws_connect(
                    'http://{}:{}{}'.format(ATTR_MESSAGE_BUS_ADDRESS,
                                            ATTR_MESSAGE_BUS_PORT,
                                            URL_TEST)),
                timeout=10)
        except asyncio.TimeoutError:
            raise FatalTestFailException(
                "Error connecting to websocket server")
        except Exception as err:
            LOGGER.error(err)
            raise
        self._bus.add_async_task(self.ws_loop())

    async def parser(self, msg):
        try:
            _data = json.loads(msg.data)
            _type = _data['type']
        except JSONDecodeError as err:
            LOGGER.error(err)
        else:
            if _type == MSG_TYPE_STOP_TEST:
                #await self.ws_connection.close()
                raise FatalTestFailException("Stop test signal received.")

    async def ws_loop(self):
        try:
            async for msg in self.ws_connection:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.parser(msg)
                elif msg.type == aiohttp.WSMsgType.CLOSED:
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

        except asyncio.CancelledError:
            LOGGER.info("closing websocket listener")

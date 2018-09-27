"""Websocket server for inter process communication"""

import asyncio
import json
import logging
from enum import Enum
from json import JSONDecodeError
from typing import Optional

import aiohttp
from aiohttp import ClientConnectionError, client_exceptions

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import (
    BaseDataHandler
)
from batterytester.core.helpers.helpers import (
    FatalTestFailException,
    TestSetupException,
)
from batterytester.core.helpers.message_data import (
    to_serializable,
    AtomWarmup,
    TestSummary,
    Message,
    LoopWarmup,
)
from batterytester.core.helpers.message_subjects import Subscriptions
from batterytester.server.server import URL_TEST, MSG_TYPE_STOP_TEST

URL_CLOSE = "close"
URL_ATOM = "atom"  # General info about the current atom.
# URL_TEST = 'test'  # General test information.

LOGGER = logging.getLogger(__name__)

KEY_PASS = "passed"
KEY_FAIL = "failed"
ATTR_FAILED_IDS = "failed_ids"


class ConnectionState(Enum):
    UNDEFINED = 0
    CONNECTING = 1
    CLOSING = 2
    RESETTING = 3
    CONNECTED = 4


class Messaging(BaseDataHandler):
    """Websocket messaging.

    Needs a running websocket server to connect and interact with."""

    def __init__(
        self,
        *,
        host="127.0.0.1",
        port=8567,
        subscriptions: Optional[Subscriptions] = None
    ):
        """

        :param host: Web(socket) server address (182.167.24.3)
        :param port: Socket port.
        """
        super().__init__(subscriptions=subscriptions)
        self.ws_connection = None
        self.session = None
        # todo: move the test summary to the server part.
        self.test_summary = TestSummary()
        self.test_summary.cache = True
        self._host = host
        self._port = port
        self._server_address = None
        self._connection_state = ConnectionState.UNDEFINED
        self._ws_connection_handler = None

    async def shutdown(self, bus):
        LOGGER.info("Messaging shutdown signal received.")
        self._connection_state = ConnectionState.CLOSING
        await self._ws_close()
        # self._ws_reader_cancel()

    def event_loop_warmup(self, testdata: LoopWarmup):
        testdata.subj = subj.LOOP_WARMUP
        self._send_to_ws(testdata)

    # def loop_warmup(self, subject, data: LoopData):
    #     data.subj = subject
    #     self._send_to_ws(data)

    def event_atom_warmup(self, testdata: AtomWarmup):
        super().event_atom_warmup(testdata)
        testdata.subj = subj.ATOM_WARMUP
        self._send_to_ws(testdata)

    # def _atom_warmup(self, subject, data: AtomData):
    #     super()._atom_warmup(subject, data)
    #     data.subj = subject
    #     self._send_to_ws(data)

    def event_test_warmup(self, testdata):
        LOGGER.debug(
            "warmup test: {} data: {}".format(subj.TEST_WARMUP, testdata)
        )
        testdata.subj = subj.TEST_WARMUP
        self._send_to_ws(testdata)

    # def test_warmup(self, subject, data: TestData):
    #     LOGGER.debug("warmup test: {} data: {}".format(subject, data))
    #     data.subj = subject
    #     self._send_to_ws(data)



    def event_test_fatal(self, testdata):
        testdata.subj = subj.TEST_FATAL
        self._send_to_ws(testdata)

    #
    # def test_fatal(self, subject, data: FatalData):
    #     data.subj = subject
    #     self._send_to_ws(data)

    def event_test_finished(self, testdata):
        testdata.subj = subj.TEST_FINISHED
        self._send_to_ws(testdata)

    # def test_finished(self, subject, data: TestFinished):
    #     data.subj = subject
    #     self._send_to_ws(data)

    def event_atom_result(self, testdata):
        """Sends out a summary of the current running test result."""
        if testdata.passed.value:
            self.test_summary.atom_passed()
        else:
            self.test_summary.atom_failed(
                self._current_idx,
                self._current_loop,
                self._atom_name,
                testdata.reason.value,
            )

        self._send_to_ws(self.test_summary)

    # def atom_result(self, subject, data: AtomResult):
    #     """Sends out a summary of the current running test result."""
    #     if data.passed.value:
    #         self.test_summary.atom_passed()
    #     else:
    #         self.test_summary.atom_failed(
    #             self._current_idx,
    #             self._current_loop,
    #             self._atom_name,
    #             data.reason.value,
    #         )
    #
    #     self._send_to_ws(self.test_summary)

    def event_sensor_data(self, testdata):
        self._send_to_ws(testdata)

    # def test_data(self, subject, data):
    #     self._send_to_ws(data)

    def event_atom_execute(self, testdata):
        testdata.subj = subj.ATOM_EXECUTE
        self._send_to_ws(testdata)

    def event_atom_collecting(self, testdata):
        testdata.subj = subj.ATOM_COLLECTING
        self._send_to_ws(testdata)

    def _send_to_ws(self, data: Message):
        _js = json.dumps(data, default=to_serializable)

        if self.ws_connection:
            task = asyncio.ensure_future(self.ws_connection.send_str(_js))
            task.add_done_callback(self._send_finished)
        else:
            LOGGER.warning("Socket connection to server is not available.")

    def _send_finished(self, future):
        try:
            val = future.result()
        except Exception as err:
            LOGGER.exception(err)
            self._connection_state = ConnectionState.RESETTING
            asyncio.ensure_future(self._ws_close())

    async def setup(self, test_name, bus):
        self._bus = bus
        self._server_address = "http://{}:{}{}".format(
            self._host, self._port, URL_TEST
        )
        self._connection_state = ConnectionState.CONNECTING
        await self._ws_connect()
        self._bus.add_async_task(self.ws_loop())

    async def parser(self, msg):
        try:
            _data = json.loads(msg.data)
            _type = _data["type"]
        except JSONDecodeError as err:
            LOGGER.error(err)
        else:
            if _type == MSG_TYPE_STOP_TEST:
                raise FatalTestFailException("Stop test signal received.")

    async def _ws_close(self):
        LOGGER.info(
            "Closing websocket connection. Connection state: {}".format(
                self._connection_state.value
            )
        )
        if self.ws_connection is not None:
            try:
                await self.ws_connection.close()
            except Exception as err:
                LOGGER.exception(err)
        self.ws_connection = None

    async def _ws_connect(self):
        try:
            self.ws_connection = await asyncio.wait_for(
                self._bus.session.ws_connect(self._server_address), timeout=10
            )
            self._connection_state = ConnectionState.CONNECTED

        except asyncio.TimeoutError:
            self._connection_state = ConnectionState.RESETTING
            raise TestSetupException(
                "Connection to the server timed out: {}".format(
                    self._server_address
                )
            )

        except ClientConnectionError:
            self._connection_state = ConnectionState.RESETTING
            raise TestSetupException(
                "Unable to connect to: {}".format(self._server_address)
            )

        except Exception as err:
            self._connection_state = ConnectionState.RESETTING
            LOGGER.exception(err)
            raise TestSetupException(
                "Unknown error occurred: {}".format(self._server_address)
            )

    async def _ws_listen(self):
        try:
            async for msg in self.ws_connection:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await self.parser(msg)
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSED,
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.CLOSE,
                ):
                    break
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break
        except client_exceptions.ClientError as err:
            LOGGER.error("Unable to connect: %s", err)
        self._connection_state = ConnectionState.RESETTING

    async def ws_loop(self):
        try:
            _max_attempts = 5
            _connect_attempts = 0
            while _connect_attempts < _max_attempts:
                if self._connection_state == self._connection_state.CLOSING:
                    await self._ws_close()
                    break

                if self._connection_state == ConnectionState.RESETTING:
                    await self._ws_close()
                    self._connection_state = ConnectionState.CONNECTING

                if self._connection_state == ConnectionState.CONNECTING:
                    try:
                        await self._ws_connect()
                    except TestSetupException as err:
                        LOGGER.error(err)

                if self._connection_state == ConnectionState.CONNECTED:
                    await self._ws_listen()

                _connect_attempts += 1
                await asyncio.sleep(1)

            raise FatalTestFailException(
                "Unable to connect to message server."
            )
        except asyncio.CancelledError:
            LOGGER.info("Closing ws reader.")

import asyncio
from asyncio import CancelledError
from random import random
from unittest.mock import MagicMock, Mock

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.actors.base_actor import BaseActor
from batterytester.components.datahandlers.base_data_handler import \
    BaseDataHandler
from batterytester.components.sensor.connector import AsyncSensorConnector
from batterytester.components.sensor.connector.random_volt_amps_connector import \
    RandomVoltAmpsConnector
from batterytester.components.sensor.incoming_parser import IncomingParser
from batterytester.components.sensor.incoming_parser.boolean_parser import \
    BooleanParser
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.base_test import BaseTest
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import FatalTestFailException, \
    NonFatalTestFailException


def AsyncMock(*args, **kwargs):
    m = MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


class FakeActor(BaseActor):
    """A fake actor"""
    actor_type = 'fake_actor'

    def __init__(self):
        self.test_name = None
        self.open_mock = MagicMock()
        self.close_mock = MagicMock()
        self._setup = Mock()
        self._shutdown = Mock()

    async def open(self, *args, **kwargs):
        self.open_mock(*args, **kwargs)
        print("open {}".format(self.test_name))

    async def close(self, *args, **kwargs):
        self.close_mock(*args, **kwargs)
        print("close {}".format(self.test_name))

    async def open_with_reponse(self, *args, **kwargs):
        self.open_mock(*args, **kwargs)
        return {"response": "test"}

    async def raise_unknown_exception(self, *args, **kwargs):
        raise Exception("Fake exception raised.")

    async def raise_fatal_test_exception(self, *args, **kwargs):
        raise FatalTestFailException("Fatal exception raised.")

    async def raise_non_fatal_test_exception(self, *args, **kwargs):
        raise NonFatalTestFailException("Non fatal exception raised.")

    async def setup(self, test_name: str, bus: Bus):
        """Initialize method.

        Executed before starting the actual test.
        Cannot be an infinite task. Needs to return for the main test to
        start."""
        self._setup(test_name, bus)
        self.test_name = test_name

    async def shutdown(self, bus: Bus):
        self._shutdown(bus)


class FakeSensorConnector(AsyncSensorConnector):
    def __init__(self, bus: Bus):
        super().__init__(bus)

    async def async_listen_for_data(self):
        """Create a volt amps data sensor."""
        try:
            while True:
                _volts = random()
                _amps = random()
                _message = ('v;{};{}\n'.format(_volts, _amps)).encode()
                await self.raw_sensor_data_queue.put(_message)
                await asyncio.sleep(0.1)
        except CancelledError:
            return


class FakeLedGateConnector(AsyncSensorConnector):
    def __init__(self, bus: Bus, delay=1.0):
        self._delay = delay
        super().__init__(bus)

    async def async_listen_for_data(self, *args):
        """Periodically send out boolean values"""
        try:
            pins = (5, 4)
            while True:
                for pin in pins:
                    _message = '{}:1'.format(pin)
                    await self.raw_sensor_data_queue.put(_message)
                    await asyncio.sleep(self._delay)
        except CancelledError:
            return


class FakeBoundSensorConnector(AsyncSensorConnector):
    """Sensor connect which sends out a fixed amount of data."""

    def __init__(self, bus: Bus, counts):
        super().__init__(bus)
        self.counts = counts

    async def async_listen_for_data(self):
        """Create a volt amps data sensor."""
        try:
            for _ in range(self.counts):
                _volts = random()
                _amps = random()
                _message = ('v;{};{}\n'.format(_volts, _amps)).encode()
                await self.raw_sensor_data_queue.put(_message)
                await asyncio.sleep(0.1)
        except CancelledError:
            return


class FakeVoltsAmpsSensor(Sensor):
    async def setup(self, test_name: str, bus: Bus):
        self._connector = RandomVoltAmpsConnector(bus)
        self._sensor_data_parser = VoltAmpsIrParser(bus)
        return await super().setup(test_name, bus)


class FakeLedGateSensor(Sensor):
    async def setup(self, test_name: str, bus: Bus):
        self._connector = FakeLedGateConnector(bus, delay=0.1)
        self._sensor_data_parser = BooleanParser(bus)
        return await super().setup(test_name, bus)


class FakeBaseTest(BaseTest):

    def handle_sensor_data(self, sensor_data: dict):
        super().handle_sensor_data(sensor_data)


class FakeDataHandler(BaseDataHandler):
    def __init__(self):
        super().__init__()
        self.calls = []
        self.setup = AsyncMock()
        self.shutdown = AsyncMock()

    def get_subscriptions(self):
        return (
            (subj.TEST_FINISHED, self.notify),
            (subj.TEST_RESULT, self.notify),
            (subj.TEST_WARMUP, self.notify),
            (subj.ACTOR_EXECUTED, self.notify),
            (subj.ACTOR_RESPONSE_RECEIVED, self.notify),
            (subj.ATOM_FINISHED, self.notify),
            (subj.ATOM_WARMUP, self.notify),
            (subj.ATOM_STATUS, self.notify),
            (subj.ATOM_RESULT, self.notify),
            (subj.RESULT_SUMMARY, self.notify),
            (subj.LOOP_WARMUP, self.notify),
            (subj.LOOP_FINISHED, self.notify),
            (subj.SENSOR_DATA, self.notify),
            (subj.TEST_FATAL, self.notify),
        )

    def notify(self, subject, data):
        self.calls.append(subject)

    async def setup(self, test_name: str, bus: Bus):
        pass


class FatalDataHandler(FakeDataHandler):
    def __init__(self, fail_subj=None):
        super().__init__()
        self.fail_subj = fail_subj

    def notify(self, subject, data):
        super().notify(subject, data)
        if subject == self.fail_subj:
            raise FatalTestFailException("{} failed.".format(subject))


class FatalSensorConnector1(AsyncSensorConnector):
    """Raises exception while listening for data"""

    async def async_listen_for_data(self, *args):
        raise FatalTestFailException()


class FatalSensorParser(IncomingParser):
    def process(self, raw_incoming):
        raise Exception("Processing problem")


class FatalSensorAsyncListenForData(Sensor):
    """A sensor which raises an exception while listening for
    sensor data."""

    async def setup(self, test_name: str, bus: Bus):
        self._connector = FatalSensorConnector1(bus)
        self._sensor_data_parser = FatalSensorParser(bus)
        await super().setup(test_name, bus)


class FatalSensorProcess(Sensor):
    """A sensor which raises an exception while processing
    incoming raw sensor data."""

    async def setup(self, test_name: str, bus: Bus):
        self._connector = FakeSensorConnector(bus)
        self._sensor_data_parser = FatalSensorParser(bus)
        await super().setup(test_name, bus)

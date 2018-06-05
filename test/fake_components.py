import asyncio
from asyncio import CancelledError
from random import random
from unittest.mock import MagicMock, Mock

from batterytester.components.actors.base_actor import BaseActor
from batterytester.components.datahandlers.base_data_handler import \
    BaseDataHandler
from batterytester.components.sensor.connector import AsyncSensorConnector
from batterytester.components.sensor.incoming_parser.boolean_parser import \
    BooleanParser
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.base_test import BaseTest
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import FatalTestFailException, \
    NonFatalTestFailException


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
        self.open_mock(*args, *kwargs)
        print("open {}".format(self.test_name))

    async def close(self, *args, **kwargs):
        self.close_mock(*args, **kwargs)
        print("close {}".format(self.test_name))

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
        self._connector = FakeSensorConnector(bus)
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
    pass

import asyncio
from asyncio import CancelledError
from random import random
from unittest.mock import MagicMock

from batterytester.core.actors.base_actor import BaseActor
from batterytester.core.bus import Bus
from batterytester.core.sensor import Sensor
from batterytester.core.sensor.connector import AsyncSensorConnector
from batterytester.core.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser
from batterytester.main_test.base_test import BaseTest


class FakeActor(BaseActor):
    """A fake actor"""
    actor_type = 'fake_actor'

    def __init__(self):
        self.test_name = None
        self.open_mock = MagicMock()
        self.close_mock = MagicMock()

    async def open(self, *args, **kwargs):
        self.open_mock(*args, *kwargs)
        print("open {}".format(self.test_name))

    async def close(self, *args, **kwargs):
        self.close_mock(*args, **kwargs)
        print("close {}".format(self.test_name))

    async def setup(self, test_name: str, bus: Bus):
        """Initialize method.

        Executed before starting the actual test.
        Cannot be an infinite task. Needs to return for the main test to
        start."""
        self.test_name = test_name


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
    def setup(self, test_name: str, bus: Bus):
        self._connector = FakeSensorConnector(bus)
        self._sensor_data_parser = VoltAmpsIrParser(bus)
        return super().setup(test_name, bus)


class FakeBaseTest(BaseTest):

    def handle_sensor_data(self, sensor_data: dict):
        super().handle_sensor_data(sensor_data)

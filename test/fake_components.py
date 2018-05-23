import asyncio
from asyncio import CancelledError
from random import random
from unittest.mock import MagicMock

from batterytester.components.actors.base_actor import BaseActor
from batterytester.components.sensor.connector import AsyncSensorConnector
from batterytester.components.sensor.incoming_parser.boolean_parser import \
    BooleanParser
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.base_test import BaseTest
from batterytester.core.bus import Bus


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

    async def raise_exception(self, *args, **kwargs):
        raise Exception("Fake exception raised.")

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

# class FakeServer():
# if sys.platform == 'win32':
#     loop = asyncio.ProactorEventLoop()
#     asyncio.set_event_loop(loop)
# else:
#     loop = asyncio.get_event_loop()
# server = Server(
#     config_folder='',
#     loop_=loop)
# server.start_server()
# try:
#     loop.run_forever()
# except KeyboardInterrupt:
#     pass
# finally:
#     loop.run_until_complete(server.stop_data_handler())
# loop.close()

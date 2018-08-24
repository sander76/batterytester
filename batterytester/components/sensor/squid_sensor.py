import asyncio
import logging
from asyncio import CancelledError

from batterytester.components.sensor.connector.squid_connector import (
    AltArduinoConnector
)
from batterytester.components.sensor.incoming_parser.squid_parser import (
    DictParser
)
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.bus import Bus, BusState
from batterytester.core.helpers.helpers import SquidConnectException

_LOGGER = logging.getLogger(__name__)


class BaseSquidSensor(Sensor):
    """Base squid sensor."""

    def __init__(self, serial_port, serial_speed=115200, sensor_prefix=None):
        super().__init__(sensor_prefix=sensor_prefix)
        self.serialport = serial_port
        self.serialspeed = serial_speed

    async def setup(self, test_name, bus):
        await super().setup(test_name, bus)

    async def _parser(self):
        """Long running task. Checks the raw data queue, parses it and
        puts data into the sensor_data_queue."""

        try:
            while True:  # self.bus.running:
                _raw_data = await self._connector.raw_sensor_data_queue.get()
                self._sensor_data_parser.chop(_raw_data)
        except CancelledError:
            _LOGGER.info("Stopped data parser")
        except Exception:
            _LOGGER.error("Data parser encountered and error")
            raise


class SquidDetectorSensor(BaseSquidSensor):
    """Detect any connected squid and reports it.

    Convenience sensor for setting up a test."""

    def __init__(self, *, serial_port, serial_speed=115200):
        super().__init__(serial_port, serial_speed, sensor_prefix=serial_port)

    async def setup(self, test_name: str, bus: Bus):
        self._connector = AltArduinoConnector(
            bus=bus, serial_port=self.serialport, serial_speed=self.serialspeed
        )
        self._sensor_data_parser = DictParser(
            bus, self.sensor_data_queue, self.sensor_prefix
        )

        async def add_connect_task():
            await asyncio.sleep(5)
            if not self.bus._state == BusState.shutting_down:
                try:
                    await self._connector.setup(test_name, bus)
                    self._connector.get_version()
                except SquidConnectException:
                    self._bus.add_async_task(add_connect_task())

        try:
            await super().setup(test_name, bus)
            self._connector.get_version()
        except SquidConnectException:
            self._bus.add_async_task(add_connect_task())

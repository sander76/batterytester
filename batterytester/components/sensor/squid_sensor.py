import asyncio

from batterytester.components.sensor.connector.arduino_connector import (
    SquidConnector
)
from batterytester.components.sensor.incoming_parser.raw_data_parser import (
    RawDataParser
)
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import SquidConnectException


class SquidSensor(Sensor):
    def __init__(
        self, *, serial_port, serial_speed=115200, sensor_prefix=None
    ):
        super().__init__(sensor_prefix=sensor_prefix)
        self.serialport = serial_port
        self.serialspeed = serial_speed

    async def setup(self, test_name: str, bus: Bus):
        self._connector = SquidConnector(
            bus=bus, serial_port=self.serialport, serial_speed=self.serialspeed
        )
        self._sensor_data_parser = RawDataParser(bus, self.serialport)

        async def add_connect_task():
            await asyncio.sleep(5)
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

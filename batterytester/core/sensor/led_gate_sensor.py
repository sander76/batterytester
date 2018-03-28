"""Ledgate sensor.

When the sensor is open it will return True.
if sensor is blocked it will return False.
"""
from batterytester.core.bus import Bus
from batterytester.core.sensor import Sensor
from batterytester.core.sensor.connector.async_threaded_serial_connector import \
    ThreadedSerialSensorConnector
from batterytester.core.sensor.incoming_parser.boolean_parser import \
    BooleanParser


class LedGateSensor(Sensor):
    def __init__(self, *, serial_port, serial_speed, sensor_name=None):
        super().__init__(sensor_name=sensor_name)
        self.serialport = serial_port
        self.serialspeed = serial_speed

    async def setup(self, test_name: str, bus: Bus):
        self._connector = ThreadedSerialSensorConnector(
            bus, self.serialport, self.serialspeed)
        self._sensor_data_parser = BooleanParser(bus)
        super().setup(test_name, bus)

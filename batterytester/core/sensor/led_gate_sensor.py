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
    """Led gate sensor. Detects whether ledgate sensor is opened (True) or closed (False)

    Expecting incoming bytes in form of "a:0" or "a:1"
    a is the sensor name. 0 or 1 is the boolean value.
    Incoming sensor data is parsed and emitted in the form of:



    {'sensor_name':{'v':True/False}}

    """

    def __init__(self, *, serial_port, serial_speed, sensor_name=None):
        """Initialize the ledgate sensor

        :param serial_port: Serial port where sensor is connected to.
        :param serial_speed: Serial port speed.
        :param sensor_name: Optional. Add an extra name to prevent duplicates
            or for better identification.
        """
        super().__init__(sensor_name=sensor_name)
        self.serialport = serial_port
        self.serialspeed = serial_speed

    async def setup(self, test_name: str, bus: Bus):
        self._connector = ThreadedSerialSensorConnector(
            bus, self.serialport, self.serialspeed)
        self._sensor_data_parser = BooleanParser(bus)
        await super().setup(test_name, bus)

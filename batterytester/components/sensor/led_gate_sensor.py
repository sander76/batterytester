"""Ledgate sensor.

When the sensor is open it will return True.
if sensor is blocked it will return False.
"""
from batterytester.components.sensor.connector.arduino_connector import \
    ArduinoConnector
from batterytester.components.sensor.incoming_parser.boolean_parser import \
    BooleanParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.bus import Bus


class LedGateSensor(Sensor):
    """Led gate sensor. Detects whether ledgate sensor is opened (True) or closed (False)

    Expecting incoming bytes in form of "a:0" or "a:1"
    a is the sensor name. 0 or 1 is the boolean value.

    If using the arduino sensors sensor names "4","5","6","7" corresponding
    to the connected digital pins.

    If a sensor prefix is defined the sensor name is prefixed with that value.

    Finally the sensor is emitted in the form of

    """

    def __init__(self, *, serial_port, serial_speed=115200,
                 sensor_prefix=None):
        """Initialize the led gate sensor

        :param serial_port: Serial port where sensor is connected to.
        :param serial_speed: Serial port speed.
        :param sensor_prefix: Optional. Add an extra name to prevent duplicates
            or for better identification.
        """
        super().__init__(sensor_prefix=sensor_prefix)
        self.serialport = serial_port
        self.serialspeed = serial_speed

    async def setup(self, test_name: str, bus: Bus):
        self._connector = ArduinoConnector(
            bus=bus, serial_port=self.serialport,
            serial_speed=self.serialspeed)
        self._sensor_data_parser = BooleanParser(bus, self.sensor_prefix)
        await super().setup(test_name, bus)

    async def shutdown(self, bus: Bus):
        await super().shutdown(bus)
        await self._connector.close_method()

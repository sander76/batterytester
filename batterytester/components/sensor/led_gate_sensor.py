"""Led gate sensor.

When the sensor is open it will return True.
if sensor is blocked it will return False.
"""
from batterytester.components.sensor.connector.squid_connector import (
    AltArduinoConnector
)
from batterytester.components.sensor.incoming_parser.boolean_parser import (
    BooleanParser
)

from batterytester.components.sensor.squid_sensor import BaseSquidSensor
from batterytester.core.bus import Bus


class LedGateSensor(BaseSquidSensor):
    """Led gate sensor. Detects whether led gate sensor is opened (True) or
    closed (False)

    Expecting incoming bytes in form of "a:0" or "a:1"
    a is the sensor name. 0 or 1 is the boolean value.

    If using the arduino sensors sensor names "4","5","6","7" corresponding
    to the connected digital pins.

    If a sensor prefix is defined the sensor name is prefixed with that value.

    Finally the sensor is emitted in the form of

    """

    async def setup(self, test_name: str, bus: Bus):
        self._connector = AltArduinoConnector(
            bus=bus, serial_port=self.serialport, serial_speed=self.serialspeed
        )
        self._sensor_data_parser = BooleanParser(
            bus, self.sensor_data_queue, self.sensor_prefix
        )
        await super().setup(test_name, bus)

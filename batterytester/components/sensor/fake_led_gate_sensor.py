"""Fake Ledgate sensor.

When the sensor is open it will return True.
if sensor is blocked it will return False.
"""
from batterytester.components.sensor.connector.random_ledgate_connector import \
    RandomLedgateConnector
from batterytester.components.sensor.incoming_parser.boolean_parser import \
    BooleanParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.bus import Bus


class FakeLedGateSensor(Sensor):
    """Fake Led gate sensor. Detects whether ledgate sensor is opened (True) or closed (False)

    Expecting incoming bytes in form of "a:0" or "a:1"
    a is the sensor name. 0 or 1 is the boolean value.

    If using the arduino sensors sensor names "4","5","6","7" corresponding
    to the connected digital pins.

    If a sensor prefix is defined the sensor name is prefixed with that value.

    Finally the sensor is emitted in the form of

    """

    def __init__(self, delay=1, sensor_prefix=None):
        """Initialize the led gate sensor"""
        self._delay = delay
        super().__init__(sensor_prefix=sensor_prefix)

    async def setup(self, test_name: str, bus: Bus):
        self._connector = RandomLedgateConnector(
            bus=bus, delay=self._delay)
        self._sensor_data_parser = BooleanParser(bus, self.sensor_prefix)
        await super().setup(test_name, bus)

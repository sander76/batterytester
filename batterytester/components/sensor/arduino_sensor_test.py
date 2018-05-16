from batterytester.components.sensor.connector.arduino_connector import \
    ArduinoConnector
from batterytester.components.sensor.incoming_parser.arduino_data_parser import \
    ArduinoParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.bus import Bus


class ArduinoSensor(Sensor):
    """Fake Arduino sensor"""

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
        self._sensor_data_parser = ArduinoParser(bus, self.sensor_prefix)
        return await super().setup(test_name, bus)

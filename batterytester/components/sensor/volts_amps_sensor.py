from batterytester.components.sensor.connector.arduino_connector import \
    ArduinoConnector
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.bus import Bus


class VoltsAmpsSensor(Sensor):
    """Fake Volts Amps sensor

    For testing purposes. Emits random generated voltage and amps data.
    """

    def __init__(self, *, serial_port, serial_speed=115200,
                 sensor_prefix=None):
        """Initialize the volts amps sensor.

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
        self._sensor_data_parser = VoltAmpsIrParser(bus, self.sensor_prefix)
        await super().setup(test_name, bus)

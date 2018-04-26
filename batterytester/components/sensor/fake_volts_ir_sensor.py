from batterytester.components.sensor.connector.random_volt_amps_connector import \
    RandomVoltAmpsConnector
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser
from batterytester.components.sensor.sensor import Sensor
from batterytester.core.bus import Bus


class FakeVoltsAmpsSensor(Sensor):
    """Fake Volts Amps sensor

    For testing purposes. Emits random generated voltage and amps data.


    """

    def __init__(self, sensor_prefix=None, delay=1):
        super().__init__(sensor_prefix=sensor_prefix)
        self.delay = delay

    def setup(self, test_name: str, bus: Bus):
        self._connector = RandomVoltAmpsConnector(bus, self.delay)
        self._sensor_data_parser = VoltAmpsIrParser(bus, self.sensor_prefix)
        return super().setup(test_name, bus)

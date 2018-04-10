from batterytester.core.bus import Bus
from batterytester.core.sensor import Sensor
from batterytester.core.sensor.connector.random_volt_amps_connector import \
    RandomVoltAmpsConnector
from batterytester.core.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser


class FakeVoltsAmpsSensor(Sensor):
    def setup(self, test_name: str, bus: Bus):
        self._connector = RandomVoltAmpsConnector(bus)
        self._sensor_data_parser = VoltAmpsIrParser(bus)
        return super().setup(test_name, bus)

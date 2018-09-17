from batterytester.components.sensor.connector.squid_connector import (
    AltArduinoConnector
)

from batterytester.components.sensor.squid_sensor import BaseSquidSensor
from batterytester.core.bus import Bus
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import \
    DownSampledVoltsAmpsParser


class VoltsAmpsSensor(BaseSquidSensor):
    """Volts Amps sensor"""

    def __init__(
        self,
        serial_port,
        serial_speed=115200,
        sensor_prefix=None,
        buffer=60,
        delta_v=0.1,
        delta_a=0.5,
    ):
        super().__init__(serial_port, serial_speed, sensor_prefix)
        self.buffer = buffer
        self.delta_v = delta_v
        self.delta_a = delta_a

    async def setup(self, test_name: str, bus: Bus):
        self._connector = AltArduinoConnector(
            bus=bus, serial_port=self.serialport, serial_speed=self.serialspeed
        )
        self._sensor_data_parser = DownSampledVoltsAmpsParser(
            bus,
            self.sensor_data_queue,
            self.sensor_prefix,
            self.buffer,
            self.delta_v,
            self.delta_a,
        )

        await super().setup(test_name, bus)

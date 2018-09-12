from batterytester.components.sensor.connector.squid_connector import \
    AltArduinoConnector
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import (
    VoltAmpsIrParser
)

from batterytester.components.sensor.squid_sensor import BaseSquidSensor
from batterytester.core.bus import Bus


class VoltsAmpsSensor(BaseSquidSensor):
    """Volts Amps sensor"""

    async def setup(self, test_name: str, bus: Bus):
        self._connector = AltArduinoConnector(
            bus=bus, serial_port=self.serialport, serial_speed=self.serialspeed
        )
        self._sensor_data_parser = VoltAmpsIrParser(
            bus, self.sensor_data_queue, self.sensor_prefix
        )
        await super().setup(test_name, bus)

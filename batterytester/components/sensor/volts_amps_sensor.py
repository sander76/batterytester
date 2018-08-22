from batterytester.components.sensor.connector.squid_connector import \
    AltArduinoConnector
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import (
    VoltAmpsIrParser
)

from batterytester.components.sensor.squid_sensor import BaseSquidSensor
from batterytester.core.bus import Bus


class VoltsAmpsSensor(BaseSquidSensor):
    """Volts Amps sensor"""

    # def __init__(
    #         self, *, serial_port, serial_speed=115200, sensor_prefix=None
    # ):
    #     """Initialize the volts amps sensor.
    #
    #     :param serial_port: Serial port where sensor is connected to.
    #     :param serial_speed: Serial port speed.
    #     :param sensor_prefix: Optional. Add an extra name to prevent duplicates
    #         or for better identification.
    #     """
    #     super().__init__(serial_port, serial_speed,
    #                      sensor_prefix=sensor_prefix)

    async def setup(self, test_name: str, bus: Bus):
        self._connector = AltArduinoConnector(
            bus=bus, serial_port=self.serialport, serial_speed=self.serialspeed
        )
        self._sensor_data_parser = VoltAmpsIrParser(
            bus, self.sensor_data_queue, self.sensor_prefix
        )
        await super().setup(test_name, bus)

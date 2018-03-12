from batterytester.core.bus import Bus
from batterytester.core.datahandlers.report import Report
from batterytester.core.sensor.led_gate_sensor import LedGateSensor
from batterytester.main_test import BaseReferenceTest


class LedgateReferenceTest(BaseReferenceTest):
    """Ledgate test test ;-)"""

    def __init__(self,
                 test_name: str,
                 loop_count: int,
                 serial_port: str,
                 baud_rate: int,
                 influx_host='172.22.3.21',
                 influx_database='menc',
                 telegram_token=None,
                 telegram_chat_id=None,
                 ):
        bus = Bus(self.async_test)

        # create the sensors.
        led_gate_sensor = LedGateSensor(bus, serial_port, baud_rate)

        # create data handlers.
        # _database = Influx(bus, influx_host, influx_database, test_name)
        _report = Report(test_name)

        super().__init__(
            bus,
            test_name,
            loop_count,
            # data_handlers=[_database, _report],
            data_handlers=_report,
            learning_mode=False,
            sensor=led_gate_sensor

        )

    def handle_sensor_data(self, sensor_data: dict):
        super().handle_sensor_data(sensor_data)
        """Sensor data to be added to the active atom."""
        if self.active_atom:
            self.active_atom.sensor_data.append(sensor_data)

    def get_sequence(self):
        raise NotImplementedError

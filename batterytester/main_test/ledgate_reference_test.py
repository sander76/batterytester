import asyncio

from batterytester.core.database.influx import Influx
from batterytester.core.sensor.led_gate_sensor import LedGateSensor
from batterytester.main_test import BaseReferenceTest, get_bus


class LedgateReferenceTest(BaseReferenceTest):
    """Ledgate test test ;-)"""

    def __init__(self,
                 test_name: str,
                 loop_count: int,
                 serial_port: str,
                 baud_rate: int,
                 influx_host='172.22.3.21',
                 influx_database='menc',
                 test_location: str = None,
                 telegram_token=None,
                 telegram_chat_id=None,
                 ):
        bus = get_bus(telegram_token, telegram_chat_id, test_name)
        led_gate_sensor = LedGateSensor(bus, serial_port, baud_rate)

        _database = Influx(bus, influx_host, influx_database, test_name)
        #_database = None

        super().__init__(
            bus,
            test_name,
            loop_count,
            database=_database,
            learning_mode=False,
            sensor=led_gate_sensor,
            test_location=test_location,
            telegram_token=telegram_token,
            telegram_chat_id=telegram_chat_id
        )

    @asyncio.coroutine
    def test_warmup(self):
        pass

    def handle_sensor_data(self, sensor_data: dict):
        super().handle_sensor_data(sensor_data)
        """Sensor data to be added to the active atom."""
        if self.active_atom:
            self.active_atom.sensor_data.append(sensor_data)
        if self.database:
            self.database.add_to_database(sensor_data, self.active_atom)

    def get_sequence(self):
        raise NotImplementedError

import asyncio

from aiopvapi.helpers.aiorequest import PvApiConnectionError

from batterytester.core.database.influx import Influx
from batterytester.core.helpers.helpers import TestFailException
from batterytester.core.helpers.powerview_utils import PowerView
from batterytester.core.sensor.led_gate_sensor import LedGateSensor
from batterytester.main_test import BaseReferenceTest, get_bus


class PowerViewLedgateReferenceTest(BaseReferenceTest):
    def __init__(self,
                 test_name: str,
                 loop_count: int,
                 serial_port: str,
                 baud_rate: int,
                 hub_ip,
                 influx_host='172.22.3.21',
                 influx_database='menc',
                 test_location: str = None,
                 telegram_token=None,
                 telegram_chat_id=None,
                 ):
        bus = get_bus(telegram_token,telegram_chat_id,test_name)
        led_gate_sensor = LedGateSensor(bus, serial_port, baud_rate)

        _database = Influx(bus, influx_host, influx_database, test_name)

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
        self.powerview = PowerView(hub_ip, self.bus.loop, self.bus.session)

    @asyncio.coroutine
    def test_warmup(self):
        try:
            yield from self.powerview.get_shades()
            yield from self.powerview.get_scenes()
        except PvApiConnectionError:
            raise TestFailException("Failed to warmup the test.")

    @asyncio.coroutine
    def handle_sensor_data(self, sensor_data):
        yield from super().handle_sensor_data(sensor_data)
        """Sensor data to be added to the active atom."""
        if self.active_atom:
            self.active_atom.sensor_data.append(sensor_data)
        self.database.add_to_database(sensor_data,self.active_atom)
        # todo: add it to the influx database too.

    def get_sequence(self):
        raise NotImplementedError

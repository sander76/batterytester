import asyncio

from aiopvapi.helpers.aiorequest import PvApiConnectionError

from batterytester.connector.async_serial_connector import AsyncSerialConnector
from batterytester.helpers.helpers import TestFailException
from batterytester.helpers.powerview_utils import PowerView
from batterytester.incoming_parser.boolean_parser import BooleanParser
from batterytester.main_test import BaseReferenceTest
from batterytester.atom.boolean_reference_atom import \
    BooleanReferenceTestAtom


class PowerViewLedgateReferenceTest(BaseReferenceTest):
    def __init__(self,
                 test_name: str,
                 loop_count: int,
                 serial_port: str,
                 baud_rate: int,
                 hub_ip,
                 test_location: str = None,
                 telegram_token=None,
                 telegram_chat_id=None,

                 ):
        boolean_parser = BooleanParser(self.bus)
        sensor_data_connector = AsyncSerialConnector(
            self.bus, boolean_parser, serial_port, baud_rate)

        super().__init__(
            test_name,
            loop_count,
            learning_mode=False,
            test_location=test_location,
            telegram_token=telegram_token,
            telegram_chat_id=telegram_chat_id,
            sensor_data_connector=sensor_data_connector
        )
        self.powerview = PowerView(hub_ip, self.bus.loop, self.bus.session)

    @asyncio.coroutine
    def test_warmup(self):
        try:
            yield from self.powerview.get_shades()
            yield from self.powerview.get_scenes()
        except PvApiConnectionError:
            raise TestFailException("Failed to warmup the test.")

    @property
    def active_atom(self) -> BooleanReferenceTestAtom:
        return self._active_atom

    def handle_sensor_data(self, sensor_data):
        """Sensor data to be added to the active atom."""
        self.active_atom.sensor_data.append(sensor_data)

    def get_sequence(self):
        raise NotImplementedError

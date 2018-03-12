import asyncio
import logging
from asyncio.futures import CancelledError

from batterytester.main_test import BaseTest, get_bus

_LOGGER = logging.getLogger(__name__)


class ExampleTest(BaseTest):
    def __init__(self,
                 sensor_data_connector=None,
                 database=None):
        bus = get_bus()
        BaseTest.__init__(
            self, bus, sensor_data_connector, database)

    def handle_sensor_data(self, sensor_data):
        pass
        # _LOGGER.debug("handling incoming sensor data: %s" % sensor_data)

    async def async_test(self):
        try:
            while self.bus.running:
                _LOGGER.debug("Doing some async testing.")
                await asyncio.sleep(10)
        except CancelledError:
            _LOGGER.debug("stopping loop test")

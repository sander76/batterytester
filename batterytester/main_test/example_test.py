import asyncio

import logging
from asyncio.futures import CancelledError

from batterytester.main_test import BaseTest

_LOGGER = logging.getLogger(__name__)


class ExampleTest(BaseTest):
    def __init__(self,
                 sensor_data_connector=None,
                 database=None):
        BaseTest.__init__(
            self, sensor_data_connector, database)

    def handle_sensor_data(self, sensor_data):
        pass
        #_LOGGER.debug("handling incoming sensor data: %s" % sensor_data)

    @asyncio.coroutine
    def async_test(self):
        try:
            while self.bus.running:
                _LOGGER.debug("Doing some async testing.")
                yield from asyncio.sleep(10)
        except CancelledError:
            _LOGGER.debug("stopping loop test")
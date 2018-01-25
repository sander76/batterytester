"""A sensor consists of a connection (serial/socket etc) collecting sensor
data and a Parser which interprets the data in consumable parts"""

import asyncio
import logging

from asyncio import CancelledError
from batterytester.core.bus import Bus
from batterytester.core.sensor.connector import SensorConnector
from batterytester.core.sensor.incoming_parser import IncomingParser

_LOGGER = logging.getLogger(__name__)


class Sensor:
    def __init__(self, bus: Bus, connector: SensorConnector,
                 sensor_data_parser: IncomingParser):
        self._bus = bus
        self._connector = connector
        self._sensor_data_parser = sensor_data_parser
        # self.sensor_data_queue = asyncio.Queue(loop=self._bus.loop)
        self.sensor_data_queue = None
        self._bus.add_async_task(self._parser())

    @asyncio.coroutine
    def _parser(self):
        """Long running task. Checks the raw data queue, parses it and
        puts data into the sensor_data_queue."""

        try:
            while True:  # self.bus.running:
                _raw_data = yield from self._connector.raw_sensor_data_queue.get()
                for _measurement in self._sensor_data_parser.process(
                        _raw_data):
                    yield from self.sensor_data_queue.put(_measurement)
        except CancelledError:
            _LOGGER.info("Stopped data parser")
        except Exception as e:
            _LOGGER.exception(e)
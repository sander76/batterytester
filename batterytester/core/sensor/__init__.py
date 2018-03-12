"""A sensor consists of a connection (serial/socket etc) collecting sensor
data and a Parser which interprets the data in consumable parts"""

import logging
from asyncio import CancelledError

from batterytester.core.bus import Bus
from batterytester.core.sensor.connector import SensorConnector
from batterytester.core.sensor.incoming_parser import IncomingParser

_LOGGER = logging.getLogger(__name__)


class Sensor:
    def __init__(self, bus: Bus, connector_: SensorConnector,
                 sensor_data_parser: IncomingParser):
        self._bus = bus
        self._connector = connector_
        self._sensor_data_parser = sensor_data_parser
        self.sensor_data_queue = None
        self._bus.add_async_task(self._parser())

    async def _parser(self):
        """Long running task. Checks the raw data queue, parses it and
        puts data into the sensor_data_queue."""

        try:
            while True:  # self.bus.running:
                _raw_data = await self._connector.raw_sensor_data_queue.get()
                for _measurement in self._sensor_data_parser.process(
                        _raw_data):
                    await self.sensor_data_queue.put(_measurement)
        except CancelledError:
            _LOGGER.info("Stopped data parser")
        except Exception:
            _LOGGER.error("Data parser encountered and error")
            raise

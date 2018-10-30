import logging
from abc import ABCMeta, abstractmethod
from asyncio import CancelledError

from batterytester.core.bus import Bus

_LOGGER = logging.getLogger(__name__)


class Sensor(metaclass=ABCMeta):
    """A sensor providing feedback from the running test.
    consists of a connector and a parser.
    The connector connects to the sensor. The parser interprets
    incoming data."""

    def __init__(self, sensor_prefix=None):
        self._bus = None
        self._connector = None
        self._sensor_data_parser = None
        self.sensor_data_queue = None
        self.sensor_prefix = sensor_prefix

    @abstractmethod
    async def setup(self, test_name: str, bus: Bus):
        """Initialize method.

        Executed before starting the actual test.
        Cannot be an infinite task. Needs to return for the main test to
        start."""
        self._bus = bus
        self._bus.add_async_task(self._parser())
        await self._connector.setup(test_name, bus)

    async def shutdown(self, bus: Bus):
        """Shutdown the sensor

        Is run at the end of the test.

        :param bus: the bus.
        :return:
        """
        if self._connector:
            await self._connector.shutdown(bus)

    async def _parser(self):
        """Long running task. Checks the raw data queue, parses it and
        puts data into the sensor_data_queue."""

        try:
            while True:  # self.bus.running:
                _raw_data = await self._connector.raw_sensor_data_queue.get()
                for _measurement in self._sensor_data_parser.process(_raw_data):
                    if _measurement:
                        await self.sensor_data_queue.put(_measurement)
        except CancelledError:
            _LOGGER.info("Stopped data parser")
        except Exception:
            _LOGGER.error("Data parser encountered and error")
            raise

"""Provides a connection to incoming sensor data.

Watches for incoming sensor data and passes it on to an "incoming parser" for
further processing.

Finally the parsed incoming data is put in the sensor_data_queue
"""

import asyncio
import logging
from threading import Thread

_LOGGER = logging.getLogger(__name__)


class SensorConnector:
    def __init__(
            self,
            bus
    ):
        self.bus = bus
        self.raw_sensor_data_queue = asyncio.Queue(loop=self.bus.loop)


class AsyncSensorConnector(SensorConnector):
    def __init__(self, bus):
        super().__init__(bus)

    async def setup(self, test_name: str, bus):
        self.bus.add_async_task(self.async_listen_for_data())

    async def shutdown(self, bus):
        pass
        # await self.close_method()

    async def async_listen_for_data(self, *args):
        """Listens for incoming raw data and puts it into the
        raw_sensor_data_queue

        Example:
        ```
        try:
            while True:
                gen = ''.join(
                    random.choice(
                        string.ascii_lowercase)
                    for _ in range(10))
                await self.raw_sensor_data_queue.put(gen)
                asyncio.sleep(5)
        except CancelledError:
            return
        ```
        """
        raise NotImplemented

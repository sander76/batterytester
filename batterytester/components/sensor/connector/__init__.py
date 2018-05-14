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
        self.bus.add_async_task(self.async_listen_for_data())

        self.bus.add_closing_task(self.close_method())

    async def close_method(self):
        pass

    @asyncio.coroutine
    def async_listen_for_data(self, *args):
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


class ThreadedSensorConnector(SensorConnector):
    def __init__(
            self,
            bus):
        super().__init__(bus)
        self.t = Thread(target=self.listen_for_data)
        self.bus.add_threaded_task(self.t)
        self.bus.add_callback(self.connect)

    def connect(self):
        pass

    def stop(self):
        pass

    def listen_for_data(self):
        """Method to be run inside a separate thread continuously checking
                incoming data. When incoming data is captured it is sent
                to the process_incoming coroutine to further process it
                (like looking for proper line endings etc.)

        Example:
        ```
        while self.bus.running:
            try:
                data = self.s.read(self.s.in_waiting or 1)
                self.bus.loop.call_soon_threadsafe(self.process_incoming,
                                                   data)
            except SerialException:
                lgr.error("error reading from serial port")
                time.sleep(1)
                break
        lgr.debug("exiting serial loop")
        ```
        """
        raise NotImplemented

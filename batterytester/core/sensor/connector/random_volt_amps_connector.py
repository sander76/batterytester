import asyncio
from asyncio import CancelledError
from random import random

from batterytester.core.bus import Bus
from batterytester.core.sensor.connector import AsyncSensorConnector


class RandomVoltAmpsConnector(AsyncSensorConnector):
    """Connector which randomly generates data each x seconds."""

    def __init__(self, bus: Bus, delay=1):
        super().__init__(bus)
        self._delay = delay

    async def async_listen_for_data(self):
        """Create a volt amps data sensor."""
        try:
            while True:
                _volts = random()
                _amps = random()
                _message = ('v;{};{}\n'.format(_volts, _amps)).encode()
                await self.raw_sensor_data_queue.put(_message)
                await asyncio.sleep(self._delay)
        except CancelledError:
            return

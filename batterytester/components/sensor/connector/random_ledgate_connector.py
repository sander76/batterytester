import asyncio
from asyncio import CancelledError

from batterytester.components.sensor.connector import AsyncSensorConnector
from batterytester.core.bus import Bus


class RandomLedgateConnector(AsyncSensorConnector):
    """Connector which randomly generates data each x seconds."""

    def __init__(self, bus: Bus, delay=1):
        super().__init__(bus)
        self._delay = delay

        self._ports = {4: 0, 5: 0, 6: 0, 7: 0}

    async def async_listen_for_data(self):
        """Create random bool data."""
        try:
            while True:
                for key in self._ports.keys():
                    if self._ports[key] == 0:
                        self._ports[key] = 1
                    else:
                        self._ports[key] = 0

                    _message = (
                        "{}s:{}:{}{}".format("{", key, self._ports[key], "}")
                    ).encode()
                    await self.raw_sensor_data_queue.put(_message)
                    await asyncio.sleep(self._delay)
        except CancelledError:
            return

import asyncio
from typing import Union

from batterytester.core.atom import Atom
from batterytester.core.bus import Bus


class DataBase:
    def __init__(self, bus: Bus):
        self.bus = bus

    @asyncio.coroutine
    def _add_to_database(self, datapoint, atom: Union[None, Atom]):
        pass

    def add_to_database(self, datapoint, atom: Union[None, Atom]):
        """Adds the datapoints to the database"""
        self.bus.add_async_task(self._add_to_database(datapoint, atom))

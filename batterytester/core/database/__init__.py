import asyncio
from typing import Union

from batterytester.core.atom import Atom
from batterytester.core.bus import Bus



class DataBase:
    def __init__(self, bus: Bus):
        self.bus = bus

    @asyncio.coroutine
    def add_to_database(self, *datapoints,atom:Union(None,Atom)):
        """Adds the datapoints to the database"""
        pass

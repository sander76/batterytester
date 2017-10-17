import asyncio
from batterytester.bus import Bus

class DataBase:
    def __init__(self, bus: Bus):
        self.bus = bus

    @asyncio.coroutine
    def add_to_database(self, *datapoints):
        """Adds the datapoints to the database"""
        pass

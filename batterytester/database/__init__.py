import asyncio
import logging

from batterytester.bus import Bus

LENGTH = 30

lgr = logging.getLogger(__name__)


class DataBase:
    def __init__(self,bus:Bus):
        self.bus=bus

    @asyncio.coroutine
    def add_to_database(self, *datapoints):
        """Adds the datapoints to the database"""
        pass

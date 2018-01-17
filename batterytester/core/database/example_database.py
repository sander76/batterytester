import asyncio

import logging

from batterytester.core.database import DataBase
from batterytester.core.helpers import Bus

_LOGGER = logging.getLogger(__name__)


class ExampleDatabase(DataBase):
    def __init__(self, text_db_file, bus: Bus):
        DataBase.__init__(self,bus)
        self.buffer = []
        self.buffer_size = 100
        if text_db_file:
            self.text_database = text_db_file
            with open(self.text_database, 'w') as fl:
                fl.write("starting database\n")
        else:
            raise Exception("No file location for database defined.")

    @asyncio.coroutine
    def add_to_database(self, *datapoints):
        self.buffer.extend(datapoints)
        if self.check_buffer():
            _LOGGER.debug("writing data to database")
            with open(self.text_database, 'a') as fl:
                for datapoint in self.buffer:
                    fl.write("{}\n".format(str(datapoint)))
            self.buffer = []

    def check_buffer(self):
        if len(self.buffer) > 100:
            return True
        return False

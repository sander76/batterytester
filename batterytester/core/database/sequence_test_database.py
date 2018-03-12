import json

from batterytester.core.bus import Bus
from batterytester.core.database import DataBase


class SequenceTestDatabase(DataBase):
    def __init__(self, bus: Bus):
        super().__init__(bus)
        self._current_unit_data = []

    def set_current_unit(self, unit_data):
        self._current_unit_data = unit_data

    async def add_to_database(self, *datapoints):
        for _datapoint in datapoints:
            self._current_unit_data.append(_datapoint)

    def save(self, filename):
        with open(filename, 'w') as _fl:
            json.dump(self._current_unit_data, _fl)

    def load(self, filename):
        with open(filename, 'r') as _fl:
            _js = json.load(_fl)
        return _js

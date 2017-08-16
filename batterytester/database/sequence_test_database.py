# import asyncio
#
# from batterytester.database import DataBase
#
#
# class SequenceTestDatabase(DataBase):
#     def __init__(self):
#         DataBase.__init__(self)
#         self._current_unit_data = []
#
#     def set_current_unit(self, unit_data):
#         self._current_unit_data = unit_data
#
#     @asyncio.coroutine
#     def add_to_database(self, *datapoints):
#         for _datapoint in datapoints:
#             self._current_unit_data.append(_datapoint)

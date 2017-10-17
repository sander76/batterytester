import asyncio
import json
import logging
import os

from batterytester.helpers.constants import ATTR_LEARNING_MODE
from batterytester.helpers.sequence_test_helpers import SensorData
from batterytester.test_atom import TestAtom, get_sensor_data_name, \
    find_reference_data

SENSOR_DATA_DELTA = 'delta'
SENSOR_DATA_LENGTH = 'length'
MOVEMENTS = 'movements'
MOVEMENT_DIRECTION = 'direction'

_LOGGING = logging.getLogger(__name__)


class RefGetter:
    def __init__(self, key, attribute):
        self._key = key
        self._attribute = attribute

    def get_ref(self, results):
        _ref = results[self._key]
        _val = getattr(_ref, self._attribute)
        return _val


class SequenceTestAtom(TestAtom):
    """
    A single test atom part of a test sequence.
    """

    def __init__(
            self, name, command,
            arguments, duration, allowed_deviation_abs=3,
            allowed_deviation_rel=10,
            result_key: str = None):
        super().__init__(name, command, arguments, duration)
        self._allowed_deviation_abs = allowed_deviation_abs
        self._allowed_deviation_rel = allowed_deviation_rel

        # sensor data is stored here.
        self.sensor_data = []

        # used for storing a global property to be used by other
        # test_atoms.
        self._result_key = result_key

        # the above result key is stored in the below dict (initialized when
        # preparing the test atom (prepare_test_atom).
        self._stored_atom_results = None

    def prepare_test_atom(
            self, save_location, idx, current_loop, report, **kwargs):
        self._stored_atom_results = kwargs.get('stored_atom_results')
        self._sensor_data_file_name = get_sensor_data_name(
            save_location, idx, current_loop)
        # self.sensor_data = SensorData(report)
        super().prepare_test_atom(
            save_location, idx, current_loop, report, **kwargs)

    def report_start_test(self, **kwargs):
        super().report_start_test(**kwargs)
        """Write to report at the very start of the test."""
        learning_mode = kwargs.get(ATTR_LEARNING_MODE)
        mode = 'learning mode' if learning_mode else 'test mode'
        self.report.create_property('mode', mode)
        self.report.create_property('sensor data path',
                                    self._sensor_data_file_name)

    # def process_sensor_data(self):
    #     current_sensor_data = SensorData(self.report,
    #                                      raw_sensor_data=self.sensor_data)
    #     success = current_sensor_data.process_sensor_data()
    #     return success



# @asyncio.coroutine
# def execute(self):
#     if self._args:
#         for key, value in self._args.items():
#             if isinstance(value, RefGetter):
#                 self._args[key] = value.get_ref(self._stored_atom_results)
#     result = yield from super().execute()
#     if self._result_key:
#         # store the result in stored_atom_results.
#         self._stored_atom_results[self._result_key] = result
#
#     return result

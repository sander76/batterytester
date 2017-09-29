"""Test being performed"""

import asyncio
import logging
import os

from batterytester.helpers.constants import ATTR_RESULT, \
    ATTR_CURRENT_LOOP
from batterytester.helpers.helpers import TestFailException
from batterytester.helpers.report import Report

SENSOR_FILE_FORMAT = 'loop_{}-idx_{}.json'
_LOGGING = logging.getLogger(__name__)


def get_sensor_data_name(save_location, test_sequence_number,
                         current_loop=0):
    _fname = os.path.join(
        save_location, SENSOR_FILE_FORMAT.format(
            current_loop, test_sequence_number))
    _LOGGING.debug("saving data to %s" % _fname)
    return _fname


def find_reference_data(idx, location):
    _search = SENSOR_FILE_FORMAT.format(0, idx)

    for _file in os.listdir(location):
        if _file == _search:
            return _file
    return None


class TestAtom:
    def __init__(self, name, command, arguments, duration):
        self._name = name
        self._command = command
        self._args = arguments
        self._duration = duration
        self.report = None

    def prepare_test_atom(self, save_location, idx, current_loop,
                          report: Report,
                          **kwargs):
        self.report = report
        self._idx = idx
        self._sensor_data_file_name = get_sensor_data_name(
            save_location, idx, current_loop)

    @property
    def name(self):
        return self._name

    @property
    def duration(self):
        return self._duration

    def _report_command_result(self, result):
        self.report.H3('TEST_COMMAND')
        self.report.create_property('command', self.name)
        self.report.create_property(ATTR_RESULT, 'success')

    def report_start_test(self, **kwargs):
        current_loop = kwargs.get(ATTR_CURRENT_LOOP)

        self.report.atom_start_header()
        self.report.H3('TEST DATA')
        self.report.create_property('loop', current_loop)
        self.report.create_property('index', self._idx)
        self.report.create_property('duration', self.duration)

    @asyncio.coroutine
    def execute(self):
        """Executes the defined command."""
        if self._args:
            _result = yield from self._command(**self._args)
        else:
            _result = yield from self._command()
        if not _result:
            raise TestFailException("Error executing command.")
        self._report_command_result(_result)
        return _result

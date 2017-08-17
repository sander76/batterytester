import logging
import os

import asyncio

from batterytester.constants import RESULT_PASS, RESULT_FAIL, ATTR_RESULT, \
    ATTR_CURRENT_LOOP
from batterytester.helpers import TestFailException
from batterytester.report import Report

FILE_FORMAT = '.json'
IDX_FORMAT = 'idx_{}'
SENSOR_FILE_FORMAT = IDX_FORMAT + '-loop_{}' + FILE_FORMAT

_LOGGING = logging.getLogger(__name__)


def get_sensor_data_name(save_location, test_sequence_number,
                         current_loop=0):
    _fname = os.path.join(
        save_location, SENSOR_FILE_FORMAT.format(
            test_sequence_number, current_loop))
    _LOGGING.debug("saving data to %s" % _fname)
    return _fname


def find_reference_data(idx, location):
    _search = IDX_FORMAT.format(idx)

    for _file in os.listdir(location):
        if _file.startswith(_search):
            return _file
    return None


class TestAtom:
    def __init__(self, name, command, arguments, duration):
        self._name = name
        self._command = command
        self._args = arguments
        self._duration = duration
        self.report = None

    def prepare_test_atom(self, save_location, idx, current_loop, report,
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
        self.report.create_table(
            ('TEST COMMAND', '.'),
            ('command', self.name),
            (ATTR_RESULT, 'success')
        )

        # self.report.H2('command')
        # # self.report._output(create_property('command', self.name))
        # _result = RESULT_PASS if result else RESULT_FAIL
        # self.report.create_property_table()

    def report_start_test(self, **kwargs):
        current_loop = kwargs.get(ATTR_CURRENT_LOOP)

        self.report.H1("START TEST ATOM")

        # self.report.H2('Test data')

        self.report.create_table(
            ("TEST DATA", "."),
            ('loop', current_loop),
            ('index', self._idx))

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

"""Individual test being performed"""

import asyncio
import logging
import os
from collections import OrderedDict

from aiopvapi.helpers.aiorequest import PvApiConnectionError, PvApiError, \
    PvApiResponseStatusError

from batterytester.core.helpers.constants import ATTR_RESULT, \
    ATTR_CURRENT_LOOP, KEY_VALUE, KEY_ATOM_NAME, KEY_ATOM_DURATION, \
    RESULT_UNKNOWN, KEY_ATOM_LOOP, KEY_ATOM_INDEX, KEY_ATOM_STATUS
from batterytester.core.helpers.helpers import NonFatalTestFailException

from batterytester.core.helpers.report import Report

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


class RefGetter:
    def __init__(self, key, attribute):
        self._key = key
        self._attribute = attribute

    def get_ref(self, results):
        _ref = results[self._key]
        _val = getattr(_ref, self._attribute)
        return _val


class Atom:
    """Basic test atom.

    Starts test execution and creates a basic report."""

    def __init__(self, name, command, arguments, duration):
        self._name = name
        self._command = command
        self._args = arguments
        self._duration = duration
        self.report = None
        self._idx = None
        self._loop = None
        self._result = ''

    @property
    def loop(self):
        return self._loop

    @property
    def idx(self):
        return self._idx

    @property
    def name(self):
        return self._name

    @property
    def duration(self):
        return self._duration

    def prepare_test_atom(self, save_location, idx, current_loop,
                          report: Report,
                          **kwargs):
        self.report = report
        self._idx = idx
        self._loop = current_loop

    def get_atom_data(self):
        return OrderedDict({
            KEY_ATOM_NAME: {KEY_VALUE: self._name},
            KEY_ATOM_LOOP: {KEY_VALUE: self._loop},
            KEY_ATOM_INDEX: {KEY_VALUE: self._idx},
            KEY_ATOM_DURATION: {KEY_VALUE: self.duration},
            KEY_ATOM_STATUS: {KEY_VALUE: RESULT_UNKNOWN},

        })

    def get_atom_result(self):
        return OrderedDict({

        })

    def _report_command_result(self, result):
        self.report.H3('TEST_COMMAND')
        self.report.create_property('command', self.name)
        self.report.create_property(ATTR_RESULT, 'success')

    # def report_start_test(self, **kwargs):
    #     current_loop = kwargs.get(ATTR_CURRENT_LOOP)
    #
    #     self.report.atom_start_header()
    #     self.report.H3('TEST DATA')
    #     self.report.create_property('loop', current_loop)
    #     self.report.create_property('index', self._idx)
    #     self.report.create_property('duration', self.duration)

    @asyncio.coroutine
    def execute(self):
        #todo: store the execution of the command also in the database.
        """Executes the defined command."""
        _result = None
        try:
            if self._args:
                _result = yield from self._command(**self._args)
            else:
                _result = yield from self._command()
        except (
                PvApiConnectionError, PvApiError,
                PvApiResponseStatusError) as err:
            self._report_command_result(_result)
            raise NonFatalTestFailException(err)


class ReferenceAtom(Atom):
    """
    A single test atom part of a test sequence.
    """

    def __init__(
            self, name, command,
            arguments, duration,
            result_key: str = None):
        super().__init__(name, command, arguments, duration)
        # sensor data is stored here.
        self.sensor_data = []
        # reference sensor data to be stored here.
        self.reference_data = None
        # used for storing a global property to be used by other
        # test_atoms.
        self._result_key = result_key

        # the above result key is stored in the below dict (initialized when
        # preparing the test atom (prepare_test_atom).
        self._stored_atom_results = None

    def prepare_test_atom(
            self, save_location, idx, current_loop, report, **kwargs):
        self._stored_atom_results = kwargs.get('stored_atom_results')
        super().prepare_test_atom(
            save_location, idx, current_loop, report, **kwargs)

    def _process_sensor_data(self):
        """Perform sensor data processing."""
        pass

    def reference_compare(self) -> bool:
        """Compare sensor data with reference data"""
        self.report.H3('REFERENCE TEST')
        return False

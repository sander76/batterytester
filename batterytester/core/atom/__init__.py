"""Individual test being performed"""

import asyncio
import logging
import os

from aiopvapi.helpers.aiorequest import PvApiConnectionError, PvApiError, \
    PvApiResponseStatusError

from batterytester.core.helpers.message_data import Data, AtomData
from batterytester.core.helpers.helpers import NonFatalTestFailException

SENSOR_FILE_FORMAT = 'loop_{}-idx_{}.json'
LOGGING = logging.getLogger(__name__)


def get_sensor_data_name(save_location, test_sequence_number,
                         current_loop=0):
    _fname = os.path.join(
        save_location, SENSOR_FILE_FORMAT.format(
            current_loop, test_sequence_number))
    LOGGING.debug("saving data to %s" % _fname)
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

    def prepare_test_atom(self, idx, current_loop,
                          **kwargs):

        self._idx = idx
        self._loop = current_loop

    def get_atom_data(self):
        return AtomData(
            self.name,
            self._idx,
            self._loop,
            self._duration
        )

    @asyncio.coroutine
    def execute(self):
        """Executes the defined command."""
        _result = None
        try:
            if self._args:
                # todo: The result should be interpreted whether feedback is correct.
                _result = yield from self._command(**self._args)
            else:
                _result = yield from self._command()
        except (
                PvApiConnectionError, PvApiError,
                PvApiResponseStatusError) as err:
            LOGGING.error(err)
            raise NonFatalTestFailException(
                "A problem occurred executing the atom command.")


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
            self, idx, current_loop, **kwargs):
        self._stored_atom_results = kwargs.get('stored_atom_results')
        super().prepare_test_atom(
            idx, current_loop, **kwargs)

    def _process_sensor_data(self):
        """Perform sensor data processing."""
        LOGGING.debug("Processing sensor data.")
        pass

    def reference_compare(self) -> bool:
        """Compare sensor data with reference data"""
        return False

    def get_atom_data(self):
        _data = super().get_atom_data()
        _data.reference_data = Data(self.reference_data)
        return _data

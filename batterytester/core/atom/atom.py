import logging
import os
from typing import Union

from aiopvapi.helpers.aiorequest import PvApiConnectionError, PvApiError, \
    PvApiResponseStatusError


from batterytester.core.helpers.helpers import TestSetupException, \
    NonFatalTestFailException
from batterytester.core.helpers.message_data import AtomData

LOGGING = logging.getLogger(__name__)

# todo: merge all atoms into one.

class Atom:
    """Basic test atom."""

    def __init__(self, *, name, command, duration, arguments=None,
                 result_key: Union[str, None] = None):

        if not callable(command):
            raise TestSetupException("atom command is not callable")
        self._name = name
        self._command = command
        self._args = arguments
        self._duration = duration
        self._idx = None
        self._loop = None
        self._result = ''
        self.sensor_data = []

        # used for storing a global property to be used by other
        # test_atoms.
        self._result_key = result_key

        # the above result key is stored in the below dict (initialized when
        # preparing the test atom (prepare_test_atom).
        self._stored_atom_results = None

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

    def prepare_test_atom(self, idx, current_loop, stored_atom_results):
        self._idx = idx
        self._loop = current_loop
        self._stored_atom_results = stored_atom_results

    def get_atom_data(self):
        return AtomData(
            self.name,
            self._idx,
            self._loop,
            self._duration
        )

    def _check_args(self):
        """Checks method arguments"""
        for key, value in self._args.items():
            if isinstance(value, RefGetter):
                self._args[key] = value.get_ref(self._stored_atom_results)

    async def execute(self):
        """Executes the defined command."""
        try:
            if self._args:
                self._check_args()
                # todo: The result should be interpreted
                # whether feedback is correct.
                _result = await self._command(**self._args)
            else:
                _result = await self._command()
            if self._result_key:
                self._stored_atom_results[self._result_key] = _result
        except (
                PvApiConnectionError, PvApiError,
                PvApiResponseStatusError) as err:
            LOGGING.error(err)
            raise NonFatalTestFailException(
                "A problem occurred executing the atom command.")


SENSOR_FILE_FORMAT = 'loop_{}-idx_{}.json'


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
    def __init__(self, key, attribute=None):
        self._key = key
        self._attribute = attribute

    def get_ref(self, results):
        _ref = results[self._key]
        if self._attribute is None:
            return _ref
        if isinstance(_ref, dict):
            return _ref[self._attribute]
        else:
            _val = getattr(_ref, self._attribute)
            return _val
import logging

from batterytester.core.atom.atom import Atom
from batterytester.core.helpers.message_data import Data, TYPE_JSON, AtomResult

LOGGING = logging.getLogger(__name__)


class ReferenceAtom(Atom):
    """
    A single test atom part of a test sequence.
    """

    def __init__(
            self, *, name, command,
            duration, reference, arguments=None,
            result_key: str = None):
        super().__init__(
            name=name, command=command, arguments=arguments, duration=duration,
            result_key=result_key)
        # sensor data is stored here.
        # reference sensor data to be stored here.
        self.reference_data = reference

    def _process_sensor_data(self):
        """Perform sensor data processing."""
        LOGGING.debug("Processing sensor data.")
        pass

    def reference_compare(self) -> AtomResult:
        """Compare sensor data with reference data"""
        return AtomResult(False)

    def get_atom_data(self):
        _data = super().get_atom_data()
        _data.reference_data = Data(self.reference_data, type_=TYPE_JSON)
        return _data

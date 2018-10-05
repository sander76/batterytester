import logging

from batterytester.core.atom.reference_atom import ReferenceAtom
from batterytester.core.helpers.constants import ATTR_SENSOR_NAME, KEY_VALUE
from batterytester.core.helpers.message_data import AtomResult, Data, TYPE_BOOL

LOGGER = logging.getLogger(__name__)


class BooleanReferenceAtom(ReferenceAtom):
    def __init__(
            self,
            name,
            command,
            duration,
            reference,
            arguments=None,
            result_key: str = None,
    ):
        super().__init__(
            name=name,
            command=command,
            duration=duration,
            reference=reference,
            arguments=arguments,
            result_key=result_key,
        )

    def _process_sensor_data(self):
        """Get the most recent values of stored sensor data."""

        super()._process_sensor_data()
        _result = {}
        if self.sensor_data:
            for _measurement in self.sensor_data:
                _result[_measurement[ATTR_SENSOR_NAME]] = _measurement[
                    KEY_VALUE
                ][KEY_VALUE]

        return _result

    def reference_compare(self) -> AtomResult:
        _sensor_data = self._process_sensor_data()
        _atom_result = AtomResult(True)
        for key, value in self.reference_data.items():
            try:
                if not _sensor_data[key] == value:
                    _atom_result.passed = Data(False, type_=TYPE_BOOL)
                    _atom_result.reason = Data(
                        "Ref values don't match. ref: {} sensor: {}"
                        "".format(str(_sensor_data), str(self.reference_data))
                    )
                    return _atom_result
            except KeyError:
                _atom_result.passed = Data(False, type_=TYPE_BOOL)
                _atom_result.reason = Data(
                    "Ref data not in sensor data. ref: {} sensor: {}".format(
                        str(self.reference_data), str(_sensor_data)
                    )
                )

        return _atom_result

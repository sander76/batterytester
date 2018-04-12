import logging

from batterytester.core.atom.reference_atom import ReferenceAtom
from batterytester.core.helpers.constants import ATTR_TIMESTAMP, KEY_SUBJECT

LOGGER = logging.getLogger(__name__)


class BooleanReferenceAtom(ReferenceAtom):
    def __init__(
            self,
            name,
            command,
            duration,
            reference,
            arguments=None,
            result_key: str = None):
        super().__init__(
            name=name, command=command,
            duration=duration, reference=reference,
            arguments=arguments, result_key=result_key)

    def _process_sensor_data(self):
        super()._process_sensor_data()
        _result = {}
        if self.sensor_data:
            for _data in self.sensor_data:
                for key, value in _data.items():
                    if not key == ATTR_TIMESTAMP and not key == KEY_SUBJECT:
                        # do not take timestamps into comparison.
                        _result[key] = value
            return _result

    def reference_compare(self) -> bool:
        # todo: make a key by key comparisson. The provided reference data
        # should be source.
        _result = self._process_sensor_data()
        LOGGER.debug("Sensor data: {}".format(_result))
        return self.reference_data == _result

import logging

from batterytester.core.atom import ReferenceAtom
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
            name, command, arguments,
            duration, result_key
        )
        self.reference_data = reference

    def _process_sensor_data(self):
        super()._process_sensor_data()
        _result = {}
        if self.sensor_data:
            for _data in self.sensor_data:
                for key, value in _data.items():
                    if not key == ATTR_TIMESTAMP and not key == KEY_SUBJECT:
                        # do not take timestamps into comparisson.
                        _result[key] = value
            return _result

    def reference_compare(self) -> bool:
        _result = self._process_sensor_data()
        LOGGER.debug("Sensor data: {}".format(_result))
        return self.reference_data == _result

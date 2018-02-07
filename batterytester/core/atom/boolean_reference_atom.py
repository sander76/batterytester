import logging

from batterytester.core.atom import ReferenceAtom

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
                    _result[key] = value
            return _result

    def reference_compare(self) -> bool:

        _result = self._process_sensor_data()
        LOGGER.debug("Sensor data: {}".format(_result))
        return self.reference_data == _result

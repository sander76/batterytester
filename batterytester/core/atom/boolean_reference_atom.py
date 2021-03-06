import logging

from batterytester.core.atom.reference_atom import ReferenceAtom
from batterytester.core.helpers.constants import ATTR_SENSOR_NAME, KEY_VALUE
from batterytester.core.helpers.message_data import AtomResult

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

    def _make_message(self, message: str, sensor_data):
        return "\n".join(
            (
                message,
                "- ref:    {}".format(str(sensor_data)),
                "- sensor: {}".format(str(self.reference_data)),
                "- index:  {}".format(self.idx),
                "- loop:   {}".format(self.loop),
            )
        )

    def reference_compare(self) -> AtomResult:
        _sensor_data = self._process_sensor_data()

        _atom_result = AtomResult(True)
        for key, value in self.reference_data.items():
            try:
                if not _sensor_data[key] == value:
                    _atom_result = AtomResult(
                        passed=False,
                        reason="Reference values don't match sensor data.",
                        data={
                            "idx": self.idx,
                            "loop": self.loop,
                            "sensor": _sensor_data,
                            "ref": self.reference_data,
                        },
                    )
                    # _atom_result.passed = Data(False, type_=TYPE_BOOL)
                    # _atom_result.reason = Data(
                    #     self._make_message(
                    #         "Reference values don't match sensor data.",
                    #         _sensor_data,
                    #     )
                    # )

            except KeyError:
                _atom_result = AtomResult(
                    passed=False,
                    reason="Reference data not in actual sensor data.",
                    data={
                        "idx": self.idx,
                        "loop": self.loop,
                        "sensor": _sensor_data,
                        "ref": self.reference_data,
                    },
                )
                # _atom_result.passed = Data(False, type_=TYPE_BOOL)
                # _atom_result.reason = Data(
                #     self._make_message(
                #         "Reference data not in actual sensor data.",
                #         _sensor_data,
                #     )
                # )

        return _atom_result

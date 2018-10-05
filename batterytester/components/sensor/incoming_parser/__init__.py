"""
Incoming parser receives incoming sensor data and cleans it.
"""

from typing import Sequence

from slugify import slugify

from batterytester.core.bus import Bus
from batterytester.core.helpers.constants import KEY_VALUE, ATTR_TIMESTAMP, \
    KEY_SUBJECT, ATTR_SENSOR_NAME
from batterytester.core.helpers.helpers import FatalTestFailException, \
    get_current_timestamp
from batterytester.core.helpers.message_subjects import SENSOR_DATA


def get_measurement(sensor_name, value) -> dict:
    return {
        ATTR_SENSOR_NAME: sensor_name,
        KEY_VALUE: {KEY_VALUE: value},
        ATTR_TIMESTAMP: {KEY_VALUE: get_current_timestamp()},
        KEY_SUBJECT: SENSOR_DATA}


class IncomingParser:
    def __init__(self, bus: Bus, sensor_prefix=None):
        self.bus = bus

        if sensor_prefix is not None:
            self.sensor_prefix = slugify(str(sensor_prefix))
        else:
            self.sensor_prefix = None

    def _interpret(self, measurement) -> dict:
        """Interprets an incoming measurement and returns the result"""
        return measurement

    def process(self, raw_incoming) -> Sequence[dict]:
        """Entry point for processing raw incoming sensor data."""
        try:
            yield self._interpret(raw_incoming)
        except Exception as err:
            # should not hit, but put here to catch if needed.
            raise FatalTestFailException(err)

    def decorate_sensor_name(self, sensor_name):
        if self.sensor_prefix:
            return '{}_{}'.format(self.sensor_prefix, sensor_name)
        return sensor_name

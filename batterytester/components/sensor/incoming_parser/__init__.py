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
    def __init__(self, bus: Bus, separator=b'\n', sensor_prefix=None):
        self.bus = bus
        self.separator = separator

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

# class IncomingParserChunked(IncomingParser):
#     """Incoming data parser where data is coming in as a stream."""
#
#     def __init__(self, bus: Bus, sensor_prefix=None):
#         IncomingParser.__init__(self, bus, sensor_prefix=sensor_prefix)
#         self.incoming_retries = 2
#         self.current_retry = 0
#         self.incoming_data = bytearray()  # all incoming data.
#
#     def _extract(self) -> Generator[dict, None, None]:
#         """Extracts raw chunks of data from the stream"""
#
#         _split = self.incoming_data.split(self.separator)
#         self.incoming_data = bytearray(_split[-1])
#         for _chunk in (_split[i] for i in range(len(_split) - 1)):
#             if _chunk != b'':
#                 yield _chunk
#
#     def process(self, raw_incoming) -> Sequence[dict]:
#         """Entry point for processing raw incoming sensor data.
#         Gets called by long running task _parser inside the serial sensor
#         class.
#
#         Returns a dictionary with measurement values, timestamp and
#         'sensor_data' as subject/identifier."""
#
#         self.incoming_data.extend(raw_incoming)
#
#         for _measurement in self._extract():
#             yield self._interpret(_measurement)

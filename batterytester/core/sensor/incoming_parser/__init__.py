"""
Incoming parser receives incoming sensor data and cleans it.
"""

from typing import Sequence, Generator

from batterytester.core.bus import Bus


# def get_time_stamp():
#     return int(time() * 1000)


class IncomingParser:
    def __init__(self, bus: Bus):
        self.bus = bus
        self.separator = b'\n'

    def process(self, raw_incoming) -> Sequence[dict]:
        """Entry point for processing raw incoming sensor data."""
        raise NotImplemented


class IncomingParserChunked(IncomingParser):
    """Incoming data parser where data is coming in as a stream."""

    def __init__(self, bus: Bus):
        IncomingParser.__init__(self, bus)
        self.incoming_retries = 2
        self.current_retry = 0
        self.incoming_data = bytearray()  # all incoming data.

    def _extract(self) -> Generator[dict, None, None]:
        """Extracts raw chunks of data from the stream"""

        _split = self.incoming_data.split(self.separator)
        self.incoming_data = bytearray(_split[-1])
        for _chunk in (_split[i] for i in range(len(_split) - 1)):
            if _chunk != b'':
                # val = self._interpret(_chunk)
                # val[ATTR_TIMESTAMP] = {KEY_VALUE: get_current_timestamp()}
                # val[KEY_SUBJECT] = SENSOR_DATA
                yield _chunk

    def process(self, raw_incoming) -> Sequence[dict]:
        """Entry point for processing raw incoming sensor data.
        Gets called by long running task _parser inside the serial sensor
        class.

        Returns a dictionary with measurement values, timestamp and
        'sensor_data' as subject/identifier."""

        # Add new raw to current raw data.
        self.incoming_data.extend(raw_incoming)
        # # Raw measurement chunks go here:
        # measurement = []
        # Interpreted chunks go here:
        # clean_data = []
        # Extract raw chunks from the raw data stream
        # self._extract(measurement)

        for _measurement in self._extract():
            yield self._interpret(_measurement)
            # yield self._interpret(_measurement)
        # #     val = self._interpret(_measurement)
        #     if val is not None:
        #         clean_data.append(val)
        # return clean_data

    def _interpret(self, measurement) -> dict:
        """Interprets an incoming measurement and returns the result"""
        return measurement

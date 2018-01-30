"""
Incoming parser receives incoming sensor data and cleans it.
"""

from time import time
from typing import Sequence, Generator

from batterytester.core.bus import Bus
from batterytester.core.helpers.constants import ATTR_VALUES, ATTR_TIMESTAMP


def get_time_stamp():
    return int(time() * 1000)


class IncomingParser:
    def __init__(self, bus: Bus):
        self.bus = bus
        self.separator = b'\n'

    def process(self, raw_incoming) -> Sequence[dict]:
        """Entry point for processing raw incoming sensor data."""
        raise NotImplemented

    # def _extract(self, measurement: list):
    #     """
    #     Consumes the raw incoming data and cuts it into consumable,
    #     interpretable chunks.
    #
    #     :param measurement:
    #     :return:
    #     """
    #     try:
    #         # Look for the first separator from the start of the incoming data
    #         # Raises value error if no separator is found.
    #         _idx = self.incoming_data.index(self.separator)
    #         # Put this part to the measurement list
    #         measurement.append(
    #             Measurement(self.incoming_data[:_idx], get_time_stamp()))
    #         # Cut away that part from the incoming data byte array.
    #         self.incoming_data = self.incoming_data[_idx + 1:]
    #         # Further consume the incoming data by calling this method again.
    #         self._extract(measurement)
    #     except ValueError:
    #         # No more separator found. Any data left in the raw incoming list
    #         # interpreted when new data has come in. For now returning and
    #         # preparing for further interpretation.
    #         return


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
                val = self._interpret(_chunk)
                val[ATTR_TIMESTAMP] = get_time_stamp()
                yield val

    def process(self, raw_incoming) -> Sequence[dict]:
        """Entry point for processing raw incoming sensor data.
        Gets called by long running task _parser inside the serial sensor
        class."""

        # Add new raw to current raw data.
        self.incoming_data.extend(raw_incoming)
        # # Raw measurement chunks go here:
        # measurement = []
        # Interpreted chunks go here:
        # clean_data = []
        # Extract raw chunks from the raw data stream
        # self._extract(measurement)

        for _measurement in self._extract():
            yield _measurement
            # yield self._interpret(_measurement)
        # #     val = self._interpret(_measurement)
        #     if val is not None:
        #         clean_data.append(val)
        # return clean_data

    def _interpret(self, measurement) -> dict:
        """Interprets an incoming measurement and returns the result"""
        return measurement

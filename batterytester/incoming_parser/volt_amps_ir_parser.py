"""
Incoming parser receives incoming sensor data and cleans it.
"""

import logging

from batterytester.bus import Bus
from batterytester.incoming_parser import IncomingParser

lgr = logging.getLogger(__name__)


class VoltAmpsIrParser(IncomingParser):
    def __init__(self, bus: Bus):
        IncomingParser.__init__(self, bus)
        self.incoming_retries = 2
        self.current_retry = 0
        self.incoming_data = bytearray()  # all incoming data.
        self.separator = b'\n'

    def process(self, raw_incoming):
        """Entry point for processing raw incoming sensor data."""

        # Add new raw to current raw data.
        self.incoming_data.extend(raw_incoming)
        # Raw measument chunks go here:
        measurement = []
        # Interpreted chunks go here:
        clean_data = []
        # Extract raw chunks from the raw data stream
        self._extract(measurement)

        for _measurement in measurement:
            val = self._interpret(_measurement)
            if val is not None:
                clean_data.append(val)
        return clean_data

    def _extract(self, measurement: list):
        """
        Consumes the raw incoming data and cuts it into consumable,
        interpretable chunks.

        :param measurement:
        :return:
        """
        try:
            _idx = self.incoming_data.index(self.separator)
            measurement.append(self.incoming_data[:_idx])
            self.incoming_data = self.incoming_data[_idx + 1:]
            # further consume the raw incoming data by calling this method again.
            self._extract(measurement)
        except ValueError:
            # No more separator found. Any data left in the raw incoming list
            # interpreted when new data has come in. For now returning and
            # preparing for further interpretation.
            return

    def _interpret(self, measurement):
        _line = measurement.split(b';')
        try:
            data = {}
            if _line[0] == b'v':
                # data is voltage and amps.
                _voltage = float(_line[1])
                _amps = float(_line[2])
                data['volts'] = _voltage
                data['amps'] = _amps
            elif _line[0] == b'i':
                # data is the ir sensor.
                _ir = int(_line[1])
                data['ir'] = _ir
            return data
        except IndexError:
            lgr.info("incoming serial data is not correct: {}"
                     .format(measurement))
            return None

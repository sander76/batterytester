"""
Incoming parser receives incoming sensor data and cleans it.
"""
import asyncio

from batterytester.bus import Bus


class IncomingParser:
    def __init__(self, bus: Bus):
        self.bus = bus

    def process(self, raw_incoming) -> list:
        """Entry point for processing raw incoming sensor data."""
        raise NotImplemented


class IncomingParserChunked(IncomingParser):
    """Incoming data parser where data is coming in as a stream.
    """

    def __init__(self, bus: Bus):
        IncomingParser.__init__(self, bus)
        self.incoming_retries = 2
        self.current_retry = 0
        self.incoming_data = bytearray()  # all incoming data.
        self.separator = b'\n'

    def process(self, raw_incoming):
        """Entry point for processing raw incoming sensor data.
        Gets called by long running task _parser inside the serial connector
        class."""

        # Add new raw to current raw data.
        self.incoming_data.extend(raw_incoming)
        # Raw measurement chunks go here:
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
            # Look for the first separator from the start of the incoming data
            _idx = self.incoming_data.index(self.separator)
            # Put this part to the measurement list
            measurement.append(self.incoming_data[:_idx])
            # Cut away that part from the incoming data byte array.
            self.incoming_data = self.incoming_data[_idx + 1:]
            # Further consume the incoming data by calling this method again.
            self._extract(measurement)
        except ValueError:
            # No more separator found. Any data left in the raw incoming list
            # interpreted when new data has come in. For now returning and
            # preparing for further interpretation.
            return

    def _interpret(self, measurement):
        """Interprets an incoming measurement"""
        raise NotImplemented

import logging

from batterytester.components.sensor.incoming_parser import (
    IncomingParser,
    get_measurement,
)
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)

INFO_TYPE_SENSOR = b"s"
INFO_TYPE_INFO = b"i"

opening_char = ord(b"{")
separator_char = ord(b":")
closing_char = ord(b"}")

STATE_UNDEFINED = 0
STATE_READY = 1
STATE_FOUND_SEPARATOR = 2
STATE_FOUND_VALUE_CHAR = 3
STATE_FIND_INFO_TYPE = 4


class SquidParser(IncomingParser):
    def __init__(self, bus, sensor_queue, sensor_prefix=None):
        self.sensor_queue = sensor_queue
        super().__init__(bus, sensor_prefix=sensor_prefix)

        self.current_measurement = []
        self.current_value = []
        self.info_type = None
        self.chop_state = STATE_UNDEFINED

    def chop(self, chunk):
        # LOGGER.debug("Parsing chunk: %s", chunk)
        for _val in chunk:
            if self.chop_state == STATE_UNDEFINED:
                if _val == opening_char:
                    self.chop_state = STATE_READY

            elif self.chop_state == STATE_READY:
                if _val == separator_char:
                    self.current_measurement.append(bytes(self.current_value))
                    self.current_value = []

                elif _val == closing_char:
                    self.current_measurement.append(bytes(self.current_value))

                    # expecting at least
                    # 1. sensor type
                    # 2. Key
                    # 3. Value
                    if len(self.current_measurement) < 3:
                        self._reset()
                        raise FatalTestFailException(
                            "Sensor info of incorrect length: {}".format(
                                self.current_measurement
                            )
                        )

                    if len(self.current_measurement) % 2 == 0:
                        self._reset()
                        raise FatalTestFailException(
                            "Incorrect sensor parsing: {}".format(
                                self.current_measurement
                            )
                        )
                    self.finalize()

                    self._reset()

                else:
                    self.current_value.append(_val)

    def _reset(self):
        self.current_value = []
        self.current_measurement = []
        self.chop_state = STATE_UNDEFINED

    def finalize(self):
        """Finalize the parsed sensor data.

        To be overridden for specific parsers to cast the parsed data
        in the correct format."""
        self.sensor_queue.put_nowait(self.current_measurement)


def chop(chunk):
    info_type = chunk[0]

    vals = chunk[2:].split(b":")
    if len(vals) % 2 != 0:
        raise FatalTestFailException(
            "Incoming sensor data not correct. {}".format(chunk)
        )

    return info_type, vals


class DictParser(SquidParser):
    def finalize(self):
        _key_vals = iter(self.current_measurement)
        # skip the first one as it contains sensor type info which we
        # ignore now.
        next(_key_vals)
        dct = {
            key.decode("utf-8"): val.decode("utf-8")
            for key, val in zip(_key_vals, _key_vals)
        }
        if self.current_measurement[0] == INFO_TYPE_INFO:
            self.sensor_queue.put_nowait(
                get_measurement(self.sensor_prefix, dct)
            )
        elif self.current_measurement[0] == INFO_TYPE_SENSOR:
            self.sensor_queue.put_nowait(
                get_measurement(self.sensor_prefix + "_data", dct)
            )

#
# class RawDataParser(IncomingParser):
#     def __init__(self, bus, sensor_prefix):
#         super().__init__(bus, sensor_prefix=sensor_prefix)
#         # self.prefix = sensor_prefix
#
#     def _interpret(self, chunk) -> dict:
#         try:
#             info_type, values = chop(chunk)
#
#             _it = iter(values)
#             dct = {
#                 key.decode("utf-8"): val.decode("utf-8")
#                 for key, val in zip(_it, _it)
#             }
#             return get_measurement(self.sensor_prefix, dct)
#
#         except Exception as err:
#             LOGGER.exception(err)
#             LOGGER.error("Incorrect measurement format: %s", chunk)
#             raise FatalTestFailException

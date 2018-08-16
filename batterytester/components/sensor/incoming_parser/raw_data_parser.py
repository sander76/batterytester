import logging

from batterytester.components.sensor.incoming_parser import IncomingParser, \
    get_measurement
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


class RawDataParser(IncomingParser):

    def __init__(self, bus, sensor_prefix):
        super().__init__(bus, sensor_prefix=sensor_prefix)
        self.prefix = sensor_prefix

    def _interpret(self, chunk) -> dict:
        try:
            # todo: sensor_type is not being processed in any way.
            sensor_type = chunk[1]
            LOGGER.debug(chunk)
            vals = chunk[3:].split(b':')
            if len(vals) % 2 != 0:
                raise FatalTestFailException("Incoming sensor data incorrect.")
            _it = iter(vals)
            data = {}
            for key, val in zip(_it, _it):
                data[key.decode('utf-8')] = val.decode("utf-8")

            return get_measurement(self.prefix, data)

        except Exception:
            LOGGER.error('Incorrect measurement format: %s', chunk)
            raise FatalTestFailException

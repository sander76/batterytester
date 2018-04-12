"""Parser which evaluates to true or false."""
import logging

from batterytester.components.sensor.incoming_parser import \
    IncomingParserChunked, get_measurement
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


class BooleanParser(IncomingParserChunked):
    """Parser which get binary data and evaluates"""

    def _interpret(self, chunk) -> dict:
        """Interpret incoming raw measurement.

        Expecting data in form of a:0 or a:1
        a is the sensor name. 0 or 1 is the boolean value.

        :returns dictionary with sensor name and boolean value
        {'sensor_name':{'v':true/false}}
        """
        try:
            sensor_name, value = chunk.split(b':')
            if value == b'0':
                value = False
            else:
                value = True

            return get_measurement(
                self.decorate_sensor_name(sensor_name.decode('utf-8')), value)

        except Exception:
            LOGGER.error('Incorrect measurement format: %s', chunk)
            raise FatalTestFailException

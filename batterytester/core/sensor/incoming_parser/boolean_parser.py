"""Parser which evaluates to true or false."""
import logging

from batterytester.core.helpers.helpers import get_current_timestamp
from batterytester.core.helpers.message_subjects import SENSOR_DATA
from batterytester.core.sensor.incoming_parser import IncomingParserChunked
from batterytester.core.helpers.constants import KEY_VALUE, ATTR_TIMESTAMP, \
    KEY_SUBJECT

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
            sensorname, value = chunk.split(b':')
            if value == b'0':
                value = False
            else:
                value = True

            _val = {sensorname.decode('utf-8'): {KEY_VALUE: value},
                    ATTR_TIMESTAMP: {KEY_VALUE: get_current_timestamp()},
                    KEY_SUBJECT: SENSOR_DATA}

            return _val
        except Exception as err:
            LOGGER.warning('Incorrect measurement format: %s', chunk)
            return None

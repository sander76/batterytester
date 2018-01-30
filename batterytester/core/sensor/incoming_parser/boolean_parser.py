"""Parser which evaluates to true or false."""
import logging

from batterytester.core.sensor.incoming_parser import IncomingParserChunked

LOGGER = logging.getLogger(__name__)


class BooleanParser(IncomingParserChunked):
    """Parser which get binary data and evaluates"""

    def _interpret(self, chunk)->dict:
        """Interpret incoming raw measurement.

        Expecting data in form of a:0 or a:1
        a is the sensor name. 0 or 1 is the boolean value.

        :returns dictionary with sensor name and boolean value {name:true/false}
        """
        try:
            sensorname, value = chunk.split(b':')
            if value == b'0':
                value = False
            else:
                value = True

            _val = {sensorname.decode('utf-8'): value}
            return _val
        except Exception as err:
            LOGGER.warning('Incorrect measurement format: %s', chunk)
            return None

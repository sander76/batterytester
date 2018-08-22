"""Parser which evaluates to true or false."""
import logging

from batterytester.components.sensor.incoming_parser import get_measurement
from batterytester.components.sensor.incoming_parser.squid_parser import (
    INFO_TYPE_SENSOR,
    SquidParser,
)
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


class BooleanParser(SquidParser):
    """Parser for boolean values"""

    def finalize(self):
        """Interpret incoming raw measurement.

        Expecting data in form of s:a:0 or s:a:1

        - s means sensor data
        - a is the sensor name.
        - 0 or 1 is the boolean value.

        :returns dictionary with sensor name and boolean value
        {'sensor_name':{'v':true/false}}
        """
        try:
            if self.current_measurement[0] == INFO_TYPE_SENSOR:
                sensor_name = self.current_measurement[1]
                value = self.current_measurement[2]
                if value == b"0":
                    value = False
                else:
                    value = True

                self.sensor_queue.put_nowait(
                    get_measurement(
                        self.decorate_sensor_name(sensor_name.decode("utf-8")),
                        value,
                    )
                )
        except (IndexError, ValueError):

            raise FatalTestFailException(
                "Incorrect measurement format: {}".format(
                    self.current_measurement
                )
            )

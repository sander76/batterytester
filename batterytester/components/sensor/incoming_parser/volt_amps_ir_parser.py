"""
Incoming parser receives incoming sensor data and cleans it.
"""

import logging

from batterytester.components.sensor.incoming_parser import get_measurement
from batterytester.components.sensor.incoming_parser.squid_parser import (
    INFO_TYPE_SENSOR,
    SquidParser,
)
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


class VoltAmpsIrParser(SquidParser):
    """Volts amps parser"""

    sensor_name = "VI"

    def __init__(self, bus, sensor_queue, sensor_prefix=None):
        super().__init__(bus, sensor_queue, sensor_prefix=sensor_prefix)
        self.sensor_name = self.decorate_sensor_name(
            VoltAmpsIrParser.sensor_name
        )

    def finalize(self):
        """Cast parsed squid data to the correct type.

        Parses to: {volts: <value>,amps: <value>}

        Finally data is emitted in form of:

        val = get_measurement(self.sensor_name,{volts: 1,amps: 2})
        """

        try:
            if self.current_measurement[0] == INFO_TYPE_SENSOR:
                if not len(self.current_measurement) == 5:
                    raise FatalTestFailException(
                        "Incorrect sensor data format: {}".format(
                            self.current_measurement))

                data = {
                    "volts": float(self.current_measurement[2]),
                    "amps": float(self.current_measurement[4]),
                }

                self.sensor_queue.put_nowait(
                    get_measurement(self.sensor_name, data)
                )

        except (IndexError, ValueError):
            raise FatalTestFailException(
                "incoming volts amps data is not correct: {}".format(
                    self.current_measurement
                )
            )

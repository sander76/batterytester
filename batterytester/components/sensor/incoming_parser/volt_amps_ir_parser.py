"""
Incoming parser receives incoming sensor data and cleans it.
"""

import logging

from batterytester.components.sensor.incoming_parser import (
    IncomingParser,
    get_measurement,
)
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


class VoltAmpsIrParser(IncomingParser):
    """Volts amps parser

    Incoming data is in form of b'v:<Volts>:a:<Amps>'
    """

    sensor_name = "VI"

    def __init__(self, bus, sensor_prefix=None):
        super().__init__(bus, sensor_prefix=sensor_prefix)
        self.sensor_name = self.decorate_sensor_name(
            VoltAmpsIrParser.sensor_name
        )

    def _interpret(self, measurement):
        """Interpret incoming data.

        Incoming data as described above.
        Parses to: {volts: <value>,amps: <value>}

        Finally data is emitted in form of:

        val = get_measurement(self.sensor_name,{volts: 1,amps: 2})
        """

        try:
            _line = measurement.split(b":")
            assert len(_line) == 4
            data = {"volts": float(_line[1]), "amps": float(_line[3])}

            return get_measurement(self.sensor_name, data)

        except (IndexError, ValueError, AssertionError):
            raise FatalTestFailException(
                "incoming volts amps data is not correct: {}".format(
                    measurement
                )
            )

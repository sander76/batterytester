"""
Incoming parser receives incoming sensor data and cleans it.
"""

import logging

from batterytester.components.sensor.incoming_parser import IncomingParser, \
    get_measurement
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


# todo: incoming volt/amps data is in different format than boolean sensor data. Sanitize this !

class VoltAmpsIrParser(IncomingParser):
    """Volts amps parser

    Incoming data is in form of b'v;<Volts>;<Amps>'
    """

    sensor_name = 'VI'

    def __init__(self, bus, sensor_prefix=None):
        super().__init__(bus, sensor_prefix)
        self.sensor_name = self.decorate_sensor_name(
            VoltAmpsIrParser.sensor_name)

    def _interpret(self, measurement):
        """Interpret incoming data.

        Incoming data as described above.
        Parses to: {volts: <value>,amps: <value>}

        Finally data is emitted in form of:

        val = get_measurement(self.sensor_name,{volts: 1,amps: 2})
        """
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
            else:
                raise FatalTestFailException(
                    "Problem parsing Volts/Amps data {}".format(measurement))

            return get_measurement(self.sensor_name, data)

        except IndexError:
            LOGGER.info("incoming serial data is not correct: {}"
                        .format(measurement))
            raise FatalTestFailException(
                "Incoming serial data is not correct.")
import logging

from batterytester.incoming_parser import IncomingParserChunked

_LOGGING = logging.getLogger(__name__)

INCOMING_VALUE = 'value'
INCOMING_SEQUENCE = 'sequence'


def create_sensor_data_container(value, sequence) -> dict:
    return {INCOMING_VALUE: value,
            INCOMING_SEQUENCE: sequence}


class SequenceDataParser(IncomingParserChunked):
    def __init__(self):
        IncomingParserChunked.__init__(self)

    def _interpret(self, measurement):
        data = None
        _line = measurement.split(b';')
        try:
            data = create_sensor_data_container(
                int(_line[0]), int(_line[1])
            )

        except IndexError:
            _LOGGING.info("incoming serial data is not correct: {}"
                          .format(measurement))

        except ValueError:
            _LOGGING.exception(
                "Parse error: {} cannot be converted to int".format(
                    str(_line)))
        finally:
            return data
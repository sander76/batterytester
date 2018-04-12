import logging

from batterytester.components.sensor.incoming_parser import \
    IncomingParserChunked
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import FatalTestFailException


_LOGGING = logging.getLogger(__name__)

INCOMING_VALUE = 'value'
INCOMING_SEQUENCE = 'sequence'


def create_sensor_data_container(value, sequence) -> dict:
    return {INCOMING_VALUE: value,
            INCOMING_SEQUENCE: sequence}


class SequenceDataParser(IncomingParserChunked):
    """Data parser where data comes in at a predefined sequence.
    Testing of this data is done by checking whether sequences are in the
    right order.
            """

    def __init__(self, bus: Bus):

        self._seq = None
        self._prev_seq = None
        IncomingParserChunked.__init__(self, bus)

    def _test_sequence(self, current):
        if self._prev_seq is None:
            self._prev_seq = current
        else:
            if self._prev_seq + 1 == current:
                self._prev_seq = current
            elif current == 0:
                # current is zero, this could mean the sequence has started
                # over. The previous sequence is the total sequence count.
                if self._seq is None:
                    self._seq = self._prev_seq
                else:
                    # if not equal the sequence does not match. So the
                    # collector missed a sequence.
                    if self._seq != self._prev_seq:
                        raise FatalTestFailException(
                            'Sequence does not match {} vs {}'.format(
                                self._seq, self._prev_seq)
                        )
                self._prev_seq = current
            else:
                raise FatalTestFailException(
                    'incorrect sensor sequence previous:{} current:{}'.format(
                        self._prev_seq, current))

    def _interpret(self, measurement):
        data = None
        _line = measurement.split(b';')
        try:
            data = create_sensor_data_container(
                int(_line[0]), int(_line[1])
            )
            self._test_sequence(data[INCOMING_SEQUENCE])
        except IndexError:
            _LOGGING.info("incoming serial data is not correct: {}"
                          .format(measurement))

        except ValueError:
            _LOGGING.exception(
                "Parse error: {} cannot be converted to int".format(
                    str(_line)))
        finally:
            return data

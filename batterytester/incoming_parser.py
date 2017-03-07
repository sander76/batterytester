import logging

from batterytester.helpers import get_bus

lgr = logging.getLogger(__name__)


class IncomingParser:
    def __init__(self):
        self.incoming_retries = 2
        self.current_retry = 0
        self.incoming_data = bytearray()
        self.bus = get_bus()

    def process(self, raw_incoming):
        self.incoming_data.extend(raw_incoming)
        measurement = []
        self.extract(measurement)
        return (self.interpret(_measurement) for _measurement in measurement)

    def extract(self, measurement: list):
        try:
            _idx = self.incoming_data.index(b'\n')
            measurement.append(self.incoming_data[:_idx])
            self.incoming_data = self.incoming_data[_idx + 1:]
            self.extract(measurement)
        except ValueError:
            return

    def interpret(self, measurement):
        _line = measurement.split(b';')
        try:
            data = {}
            if _line[0] == b'v':
                # data is voltage and amps.
                _voltage = float(_line[1])
                _amps = float(_line[2])
                # yield from self.outgoing_queue.put({'volts': _voltage,
                #                        'amps': _amps})
                data['volts'] = _voltage
                data['amps'] = _amps
            elif _line[0] == b'i':
                # data is the ir sensor.
                _ir = int(_line[1])
                # yield from self.outgoing_queue.put({'ir': _ir})
                data['ir'] = _ir
            return data
        except IndexError:
            lgr.info("incoming serial data is not correct: {}"
                     .format(measurement))
            return {}
            # else:
            #     lgr.info(
            #         "incoming serial data is not correct: {}".format(measurement))
            #     if self.current_retry > self.incoming_retries:
            #         raise UserWarning("Incoming measurement data is not correct.")
            #     self.current_retry += 1

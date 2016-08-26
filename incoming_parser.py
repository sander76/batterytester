import logging

lgr = logging.getLogger(__name__)


class IncomingParser:
    def __init__(self, database, state):
        self.database = database
        self.state = state
        self.incoming_retries = 3
        self.current_retry = 0

    def parse(self, incoming):
        _line = incoming.split(b';')
        if _line[0] == b'v':
            # data is voltage and amps.
            _voltage = float(_line[1])
            _amps = float(_line[2])
            self.database.add_data(_voltage, _amps)
        elif _line[0] == b'i':
            # data is the ir sensor.
            _ir = int(_line[1])
            self.state.ir = _ir
            self.database.add_ir_data(_ir)
        else:
            lgr.info("incoming serial data is not correct: {}".format(incoming))
            if self.current_retry > self.incoming_retries:
                raise UserWarning("Incoming measurement data is not correct.")
            self.current_retry += 1

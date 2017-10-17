from batterytester.helpers.report import Report
from batterytester.incoming_parser.sequence_data_parser import INCOMING_VALUE

MOVEMENT_COUNT = 'pulse_count'
MOVEMENT_DURATION = 'duration'


def do_deltas(test_value, ref_value, do_rel=True):
    _delta_abs = test_value - ref_value
    if do_rel:
        _delta_rel = round(
            (100 / ref_value * test_value) - 100,
            1)
    else:
        _delta_rel = 'skip'
    return _delta_abs, _delta_rel


def check(test_value, ref_value, abs_deviation_allowed, rel_deviation_allowed,
          passed, do_rel=True):
    _delta_abs, _delta_rel = do_deltas(test_value, ref_value, do_rel=do_rel)
    _pass_abs = abs(_delta_abs) <= abs_deviation_allowed
    if do_rel:
        _pass_rel = abs(_delta_rel) <= rel_deviation_allowed
        _passed = passed & _pass_rel & _pass_abs
    else:
        _pass_rel = 'skip'
        _passed = passed & _pass_abs

    return (
        (ref_value, test_value, _delta_abs, _pass_abs, _delta_rel, _pass_rel),
        _passed
    )

def get_state(delta):
    _state_ = 0
    if delta > 0:
        _state_ = 1
    elif delta < 0:
        _state_ = -1
    return _state_

class Movement:
    def __init__(self, raw_sensor_data, first_sensor_data):
        """
        :param raw_sensor_data: Raw data
        :param first_sensor_data: The first raw data entry inside the testatom.
                Used for normalization purposes.
        """
        # used for normalization purposes.
        self._first = first_sensor_data
        # Can be used for calculation delta's etc.
        self.prev_sensor_data = raw_sensor_data
        self._raw = [raw_sensor_data]

    def add_raw_data(self, raw_sensor_data):
        self._raw.append(raw_sensor_data)

    def process(self):
        """Processing the raw movement data.

        Raw data has two key value pairs: INCOMING_VALUE and INCOMING_SEQUENCE
        """
        # Sensor value from where movement has started.
        self._start_pulse_abs = self._raw[0][INCOMING_VALUE]
        # The raw data count is an indication of the duration of the
        # movement as datapoints come in at a fixed frequency
        # (eg every 500 ms.)
        # outcome is -1 as first datapoint is the start of the movement.
        # No actual movement is started in the first datapoint
        self._duration = (len(self._raw)) - 1
        # The total movement defined in pulse values.
        # This is an indication of the total travel of the product.
        self._pulse_delta = (self._raw[-1][INCOMING_VALUE]
                             - self._raw[0][INCOMING_VALUE])

    def compare(self, test_movement, abs_allowed, rel_allowed):
        passed = True
        _vals_duration, passed = check(
            self._duration,
            test_movement._duration,
            abs_allowed,
            rel_allowed, passed)
        _vals_pulse_delta, passed = check(
            self._pulse_delta,
            test_movement._pulse_delta,
            abs_allowed,
            rel_allowed, passed)
        return (
                   # ('start_pulse',) + _vals_start_pulse_abs,
                   ('duration',) + _vals_duration,
                   ('pulse_count',) + _vals_pulse_delta), passed

    @staticmethod
    def get_compare_header():
        """Header for comparisson table creation

        Headers must match the values returned by ```compare``` method
        """
        return (
            'prop', 'ref', 'test', 'delta [abs]', 'pass', 'delta [%]', 'pass')

    @staticmethod
    def get_movement_header():
        """Header data for table creation.

        Headers must match the values returned by ```report_movement_data```
        """
        return (
            'pulse_start', 'duration', 'movement'
        )

    def report_movement_data(self):
        return (
            self._start_pulse_abs, self._duration, self._pulse_delta)


class SensorData:
    def __init__(self, report: Report, raw_sensor_data=None):
        if raw_sensor_data is None:
            self._raw_sensor_data = []
        else:
            self._raw_sensor_data = raw_sensor_data
        self._validated = False
        # list with individual movement data
        self._movements = []
        # offset values which are used to normalize the data starting sensor
        # data and sequence value to zero.
        self.offset = {}
        self._report = report

    def add_raw_data(self, raw_data):
        self._raw_sensor_data.append(raw_data)

    @property
    def movements(self):
        return self._movements

    def process_sensor_data(self, report=True) -> bool:
        self._bucketize()
        self._aggregate()
        if report:
            self._report_sensor_data()
        return True

    def _new_movement(self, data, previous_data):
        """Adds a new movement to the movements list.
        """
        self._movements.append(
            Movement(previous_data, self._raw_sensor_data[0]))
        self._movements[-1].add_raw_data(data)

    def _aggregate(self):
        """Aggregates separate movement buckets into summarized data"""
        for _movement in self._movements:
            _movement.process()

    def _add_value_to_current_movement(self, data):
        """Adds movement values to current movement."""
        self._movements[-1].add_raw_data(data)

    def _bucketize(self):
        """Groups sensor data into separate movement buckets.

        Sensor data is grouped inside a bucket with identical
        movement direction.
        """
        # self._do_offsets()
        _prev_data = None
        _previous_state = None

        for _data in self._raw_sensor_data:
            _val = _data[INCOMING_VALUE]
            if _prev_data is None:
                _prev_data = _data
            else:
                _delta = _val - _prev_data[INCOMING_VALUE]  # _prev_val

                _state = get_state(_delta)
                if _state == 1 or _state == -1:
                    # there is movement. data needs to be processed
                    if _previous_state == _state:
                        # state (==direction) is the same. Adding values.
                        self._add_value_to_current_movement(_data)
                    else:
                        self._new_movement(_data, _prev_data)
                    _previous_state = _state
                else:
                    _previous_state = 0
                _prev_data = _data

    def _get_movements(self):
        _table_header = ("idx",) + Movement.get_movement_header()

        rows = (
            (idx,) + rw.report_movement_data()
            for idx, rw
            in enumerate(self._movements))

        self._report.create_table(_table_header, *rows)

    def _report_sensor_data(self):
        self._report.H3("Sensor data")

        self._get_movements()

    def compare(self, other,allowed_deviation_abs,allowed_deviation_rel):
        self._report.H3('REFERENCE TEST')

        if len(self.movements) != len(other.movements):
            self._report.p(
                "Test data and reference test data don't match in length")
            self._report_sensor_data()
            return False

        _output = [('idx',) + Movement.get_compare_header()]
        _passed = None

        for idx, _movement in enumerate(self.movements):

            _values, passed = _movement.compare(
                other.movements[idx],
                allowed_deviation_abs,
                allowed_deviation_rel)
            if _passed is None:
                _passed = passed
            else:
                _passed = _passed & passed
            for _value in _values:
                _output.append((idx,) + _value)

        self._report.create_table(_output[0], *_output[1:], col1_width=None)
        self._report.test_result(_passed)

        return _passed

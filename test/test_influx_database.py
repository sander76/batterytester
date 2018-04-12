import pytest

from batterytester.components.datahandlers import Influx
from batterytester.components.datahandlers.influx import line_protocol_fields, \
    line_protocol_tags, get_time_stamp
from batterytester.components.sensor.incoming_parser import get_measurement
from batterytester.core.helpers.constants import ATTR_VALUES


@pytest.fixture
def fake_measurement1():
    meas = get_measurement('test', {'i': 10, 'b': 1.2})
    return meas


def test_line_protocol_fields(fake_measurement1):
    _out = line_protocol_fields(fake_measurement1[ATTR_VALUES][ATTR_VALUES])
    assert _out == 'i=10,b=1.2'


def test_line_protocol_tags():
    _in = {'a': 'sensor1'}
    _out = line_protocol_tags(_in)
    assert _out == ',a=sensor1'


def test_empty_time_protocol_tags():
    _in = {}
    _out = line_protocol_tags(_in)
    assert _out == ''


def test_get_time_stamp():
    _measurement = get_measurement('test_sensor', 10)
    ts = get_time_stamp(_measurement)
    assert isinstance(ts, int)


@pytest.fixture
def fake_influx():
    def fake_send(_self, data):
        return data

    influx = Influx('127.0.0.1', buffer_size=5)
    influx._send = fake_send
    return influx


def test_add_data(fake_influx):
    measurement = get_measurement('sensor1', {'val': 1})
    fake_influx._add_to_database('not_important', measurement)
    assert len(fake_influx.data) == 1

# todo: test url composition.

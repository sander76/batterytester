import pytest

from batterytester.core.datahandlers.influx import line_protocol_tags, \
    get_time_stamp, Influx
from batterytester.core.sensor.incoming_parser import get_measurement


def test_line_protocol_tags():
    _in = {'a': 1, 'b': 2}
    _out = line_protocol_tags(_in)
    assert _out == ',a=1,b=2'


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
    measurement = get_measurement('sensor1', 1)
    fake_influx._add_to_database('not_important', measurement)
    assert len(fake_influx.data) == 1

#todo: test url composition.
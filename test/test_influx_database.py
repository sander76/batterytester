from unittest.mock import MagicMock, Mock

import pytest

from batterytester.components.datahandlers import Influx
from batterytester.components.datahandlers.influx import get_time_stamp, \
    InfluxLineProtocol
from batterytester.components.sensor.incoming_parser import get_measurement
from batterytester.core.helpers.constants import ATTR_VALUES, ATTR_TIMESTAMP, \
    ATTR_SENSOR_NAME
from batterytester.core.helpers.message_data import AtomData, Data


@pytest.fixture
def fake_measurement1():
    meas = get_measurement('test', 10)
    meas[ATTR_TIMESTAMP][ATTR_VALUES] = 12345678
    return meas


@pytest.fixture
def fake_influx():
    influx = Influx(host='127.0.0.1', buffer_size=5)
    influx.bus = MagicMock()
    influx.bus.add_async_task = Mock()
    influx._send = Mock()
    influx.test_name = 'fake_test'
    influx.measurement = 'fake_test'

    return influx


@pytest.fixture
def fake_atom_data():
    atom = AtomData('atom1', 0, 0, 5)
    atom.started = Data(value=12345678)
    return atom


MEASUREMENT = 'test measurement'
SLUGGED = 'test-measurement'


def test_influx_line_protocol_notags(fake_measurement1):
    inf = InfluxLineProtocol(
        MEASUREMENT,
        fake_measurement1[ATTR_TIMESTAMP][ATTR_VALUES],
        fields={'value': fake_measurement1[ATTR_VALUES][ATTR_VALUES]})
    assert inf._measurement == SLUGGED
    _measurement = inf.create_measurement()
    assert _measurement == '{} value=10 12345678000000000'.format(SLUGGED)


def test_influx_line_protocol1_nofields(fake_measurement1):
    inf = InfluxLineProtocol(
        MEASUREMENT,
        fake_measurement1[ATTR_TIMESTAMP][ATTR_VALUES],
        tags={'value': fake_measurement1[ATTR_VALUES][ATTR_VALUES]})
    _measurement = inf.create_measurement()
    assert _measurement == '{},value=10 12345678000000000'.format(SLUGGED)


def test_get_time_stamp():
    _measurement = get_measurement('test_sensor', 10)
    ts = get_time_stamp(_measurement)
    assert isinstance(ts, int)


def test_atom_warmup(fake_influx: Influx, fake_atom_data: AtomData):
    fake_influx._atom_warmup_event('no subj', fake_atom_data)
    assert len(fake_influx.data) == 1
    _data = fake_influx.data[0]
    assert _data._measurement == 'fake-test'
    assert _data._tags is None
    assert _data._fields['title'] == 'atom warmup'
    assert _data._fields['text'] == fake_atom_data.atom_name.value
    assert _data._fields['tags'] == "loop 0,index 0"


def test_prepare_data(fake_influx: Influx, fake_atom_data):
    val = fake_influx._prepare_data()
    assert val is None
    fake_influx._atom_warmup_event('no subj', fake_atom_data)
    val = fake_influx._prepare_data()
    assert val is not None


def test_handle_sensor(fake_influx: Influx, fake_measurement1, fake_atom_data):
    fake_influx._handle_sensor('no subj', fake_measurement1)
    assert len(fake_influx.data) == 1
    _data = fake_influx.data[0]
    assert _data._measurement == 'fake-test'
    assert _data._tags == {}
    assert _data._fields == {fake_measurement1[ATTR_SENSOR_NAME]: 10}

    fake_influx._atom_warmup_event('no subj', fake_atom_data)
    fake_influx._handle_sensor('no subj', fake_measurement1)
    assert len(fake_influx.data) == 3
    _data = fake_influx.data[-1]
    assert _data._tags == {'loop': 0, 'idx': 0}


def test_flush(fake_influx: Influx, fake_measurement1):
    fake_influx._handle_sensor('no subj', fake_measurement1)
    assert len(fake_influx.data) == 1
    fake_influx._flush()
    assert len(fake_influx.data) == 0
    fake_influx._send.assert_called_once()

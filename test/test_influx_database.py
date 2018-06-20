from collections import OrderedDict
from unittest.mock import Mock

import pytest

from batterytester.components.datahandlers import Influx
from batterytester.components.datahandlers.influx import get_time_stamp, \
    InfluxLineProtocol, line_protocol_fields, nesting
from batterytester.components.sensor.incoming_parser import get_measurement
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.constants import ATTR_VALUES, ATTR_TIMESTAMP, \
    ATTR_SENSOR_NAME
from batterytester.core.helpers.message_data import AtomData, Data
from test.fake_components import FakeActor
from test.seqeuences import get_empty_sequence, get_unknown_exception_sequence


@pytest.fixture
def fake_measurement1():
    meas = get_measurement('test', 10)
    meas[ATTR_TIMESTAMP][ATTR_VALUES] = 12345678
    return meas


@pytest.fixture
def fake_measurement2():
    meas = get_measurement('vi', OrderedDict([('volts', 1.2), ('amps', 2.3)]))
    meas[ATTR_TIMESTAMP][ATTR_VALUES] = 12345678
    return meas


@pytest.fixture
def fake_tag():
    return OrderedDict([('tag1', 'abc'), ('tag2', 10)])


@pytest.fixture
def fake_atom_data():
    atom = AtomData('atom1', 0, 0, 5)
    atom.started = Data(value=12345678)
    return atom


MEASUREMENT = 'test measurement'
SLUGGED = 'test-measurement'


def test_influx_line_protocol_notags(fake_measurement1, fake_tag):
    inf = InfluxLineProtocol(
        MEASUREMENT,
        fake_measurement1[ATTR_TIMESTAMP][ATTR_VALUES],
        fields=fake_tag)
    assert inf._measurement == SLUGGED
    _measurement = inf.create_measurement()
    assert _measurement == '{} tag1="abc",tag2=10 12345678000000000'.format(
        SLUGGED)


def test_influx_line_protocol1_nofields(fake_measurement1):
    inf = InfluxLineProtocol(
        MEASUREMENT,
        fake_measurement1[ATTR_TIMESTAMP][ATTR_VALUES],
        tags={'value': fake_measurement1[ATTR_VALUES][ATTR_VALUES]})
    assert inf._measurement == SLUGGED
    _measurement = inf.create_measurement()
    assert _measurement == '{},value=10 12345678000000000'.format(SLUGGED)


def test_influx_line_protocol_nested_values(fake_measurement2):
    db = Influx()
    db.measurement = 'test-measurement'
    db.add_to_buffer = Mock()
    db._handle_sensor('nosubj', fake_measurement2)

    meas = db.add_to_buffer.call_args[0][0]
    assert meas._fields == {'vi': fake_measurement2[ATTR_VALUES][ATTR_VALUES]}

    to_line_protocol = meas.create_measurement()
    # _measurement = inf.create_measurement()
    assert 'vi_volts=1.2' in to_line_protocol
    assert 'vi_amps=2.3' in to_line_protocol


def test_line_protocol_fields():
    field = OrderedDict({'test': 'test'})
    result = line_protocol_fields(field)
    assert result == 'test="test"'

    field['value'] = 10
    result = line_protocol_fields(field)
    assert result == 'test="test",value=10'


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


def test_flush(fake_influx_nobus: Influx, fake_measurement1):
    fake_influx_nobus._handle_sensor('no subj', fake_measurement1)
    assert len(fake_influx_nobus.data) == 1
    fake_influx_nobus._flush()
    assert len(fake_influx_nobus.data) == 0


def test_shutdown(fake_influx: Influx, base_test: BaseTest, fake_measurement1):
    fake_influx._handle_sensor('no subj', fake_measurement1)
    base_test.get_sequence = get_empty_sequence
    base_test.add_data_handlers(fake_influx)

    assert len(fake_influx.data) == 1
    base_test.start_test()

    assert len(fake_influx._send.mock.mock_calls) == 1
    # fake_influx._send.mock.assert_called_once()
    assert len(fake_influx.data) == 0


def test_shutdown_test_error(
        fake_influx: Influx, base_test: BaseTest, fake_measurement1):
    fake_influx._handle_sensor('no subj', fake_measurement1)
    base_test.get_sequence = get_unknown_exception_sequence

    base_test.add_actor(FakeActor())
    base_test.add_data_handlers(fake_influx)

    assert len(fake_influx.data) == 1

    base_test.start_test()

    assert len(fake_influx._send.mock.mock_calls) == 1
    assert len(fake_influx.data) == 0


def test_nesting():
    nested = {'a':1,'b':2}
    result = {'a':1,'b':2}
    new = nesting(nested)
    for key, value in result.items():
        assert new[key] == value

    nested = {'a': 1, 'b': {'a': 2}}
    result = {'a': 1, 'b_a': 2}

    new = nesting(nested)
    for key, value in result.items():
        assert new[key] == value

    nested = {'a': 1, 'b': {'a': 2, 'b': 5}}
    result = {'a': 1, 'b_a': 2, 'b_b': 5}
    new = nesting(nested)
    for key, value in result.items():
        assert new[key] == value

    nested = {'a': 1, 'b': {'a': 2, 'b': {'b': 5}}}
    result = {'a': 1, 'b_a': 2, 'b_b_b': 5}
    new = nesting(nested)
    for key, value in result.items():
        assert new[key] == value

# todo: test when connection with database server is lost.

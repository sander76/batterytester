import pytest

from batterytester.components.sensor.incoming_parser.boolean_parser import \
    BooleanParser
from batterytester.core.helpers.constants import KEY_SUBJECT, ATTR_TIMESTAMP, \
    ATTR_VALUES, ATTR_SENSOR_NAME
from batterytester.core.helpers.helpers import FatalTestFailException


@pytest.fixture
def fake_binary_parser():
    parser = BooleanParser(None)
    return parser


def test_interpret(fake_binary_parser):
    val = fake_binary_parser._interpret(b'abvf:1')
    assert val[ATTR_SENSOR_NAME] == 'abvf'

    assert val[ATTR_VALUES] == {'v': True}
    assert KEY_SUBJECT in val
    assert ATTR_TIMESTAMP in val
    val = fake_binary_parser._interpret(b'abcc:0')
    assert val[ATTR_SENSOR_NAME] == 'abcc'
    assert val[ATTR_VALUES] == {'v': False}


def test_false_interpret(fake_binary_parser):
    with pytest.raises(FatalTestFailException):
        fake_binary_parser._interpret(b'abvf')


def test_sensor_name():
    parser = BooleanParser(None, sensor_prefix='test_sensor')
    val = parser._interpret(b'abcd:1')
    assert val[ATTR_SENSOR_NAME] == 'test_sensor_abcd'
    val = parser._interpret(b'def:0')
    assert val[ATTR_SENSOR_NAME] == 'test_sensor_def'
    assert val[ATTR_VALUES] == {'v': False}

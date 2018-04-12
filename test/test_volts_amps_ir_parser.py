import pytest

from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import \
    VoltAmpsIrParser
from batterytester.core.helpers.constants import KEY_SUBJECT, ATTR_TIMESTAMP, \
    ATTR_SENSOR_NAME, ATTR_VALUES
from batterytester.core.helpers.helpers import FatalTestFailException



# todo: finish these tests.

@pytest.fixture
def fake_volt_amps_parser():
    parser = VoltAmpsIrParser(None)
    return parser


def test_interpret(fake_volt_amps_parser):
    val = fake_volt_amps_parser._interpret(b'v;1;3')
    assert val[ATTR_SENSOR_NAME] == 'VI'
    assert val[ATTR_VALUES] == {'v': {'amps': 3, 'volts': 1}}
    assert KEY_SUBJECT in val
    assert ATTR_TIMESTAMP in val


def test_false_interpret(fake_volt_amps_parser):
    with pytest.raises(FatalTestFailException):
        fake_volt_amps_parser._interpret(b'abvf')

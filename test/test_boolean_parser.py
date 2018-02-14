import pytest

from batterytester.core.helpers.constants import KEY_SUBJECT, ATTR_TIMESTAMP
from batterytester.core.sensor.incoming_parser.boolean_parser import \
    BooleanParser


@pytest.fixture
def fake_binary_parser():
    parser = BooleanParser(None)
    return parser


def test_interpret(fake_binary_parser):
    val = fake_binary_parser._interpret(b'abvf:1')
    assert val['abvf'] == {'v': True}
    assert KEY_SUBJECT in val
    assert ATTR_TIMESTAMP in val
    val = fake_binary_parser._interpret(b'abcc:0')
    assert val['abcc'] == {'v': False}


def test_false_interpret(fake_binary_parser):
    val = fake_binary_parser._interpret(b'abvf')
    assert val is None

import pytest

from batterytester.incoming_parser.boolean_parser import BooleanParser


@pytest.fixture
def fake_binary_parser():
    parser = BooleanParser(None)
    return parser

def test_interpret(fake_binary_parser):
    val = fake_binary_parser._interpret(b'abvf:1')
    assert val == {'abvf':True}
    val = fake_binary_parser._interpret(b'abcc:0')
    assert val == {'abcc':False}

def test_false_interpret(fake_binary_parser):
    val = fake_binary_parser._interpret(b'abvf')
    assert val is None
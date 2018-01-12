from unittest.mock import MagicMock

import pytest

from batterytester.incoming_parser import IncomingParserChunked


@pytest.fixture
def fake_parser_chunked(monkeypatch):
    def interpreter(input):
        return input

    parser = IncomingParserChunked(None)
    monkeypatch.setattr(parser, '_interpret', interpreter)
    return parser


def test_extract1(fake_parser_chunked):
    measurement = []
    fake_parser_chunked.incoming_data.extend(b'abc\n')
    fake_parser_chunked._extract(measurement)
    assert measurement[0].values == b'abc'
    assert fake_parser_chunked.incoming_data == b''


def test_extract2(fake_parser_chunked):
    measurement = []
    fake_parser_chunked.incoming_data.extend(b'abd\naa')
    fake_parser_chunked._extract(measurement)
    assert measurement[0].values == b'abd'
    assert fake_parser_chunked.incoming_data == b'aa'


def test_extract3(fake_parser_chunked):
    measurement = []
    fake_parser_chunked.incoming_data.extend(b'abk\naa\naaa')
    fake_parser_chunked._extract(measurement)
    assert measurement[0].values == b'abk'
    assert measurement[1].values == b'aa'
    assert fake_parser_chunked.incoming_data == b'aaa'


def test_extract4(fake_parser_chunked):
    measurement = []
    fake_parser_chunked.incoming_data.extend(b'\n')
    fake_parser_chunked._extract(measurement)
    assert measurement, [b'']
    assert fake_parser_chunked.incoming_data == b''


def test_process(fake_parser_chunked):
    val = fake_parser_chunked.process(b'abc')
    assert val == []
    val = fake_parser_chunked.process(b'\n')
    assert val[0].values == b'abc'

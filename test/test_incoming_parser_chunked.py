import pytest

from batterytester.core.sensor.incoming_parser import IncomingParserChunked


@pytest.fixture
def fake_parser_chunked(monkeypatch):
    def interpreter(input):
        return {'inp': input}

    parser = IncomingParserChunked(None)
    monkeypatch.setattr(parser, '_interpret', interpreter)
    return parser


def test_extract1(fake_parser_chunked):
    fake_parser_chunked.incoming_data.extend(b'abc\n')
    for idx, val in enumerate(fake_parser_chunked._extract()):
        if idx == 0:
            assert val == b'abc'
    assert fake_parser_chunked.incoming_data == b''


def test_extract2(fake_parser_chunked):
    fake_parser_chunked.incoming_data.extend(b'abd\naa')
    for idx, val in enumerate(fake_parser_chunked._extract()):
        if idx == 0:
            assert val == b'abd'
    assert fake_parser_chunked.incoming_data == b'aa'


def test_extract3(fake_parser_chunked):
    fake_parser_chunked.incoming_data.extend(b'abk\naa\naaa')
    for idx, val in enumerate(fake_parser_chunked._extract()):
        if idx == 0:
            assert val == b'abk'
        elif idx == 1:
            assert val == b'aa'
    assert isinstance(fake_parser_chunked.incoming_data, bytearray)
    assert fake_parser_chunked.incoming_data == b'aaa'


def test_extract4(fake_parser_chunked):
    fake_parser_chunked.incoming_data.extend(b'\n')
    for idx, val in enumerate(fake_parser_chunked._extract()):
        assert False
    assert isinstance(fake_parser_chunked.incoming_data, bytearray)
    assert fake_parser_chunked.incoming_data == b''


def test_empty_byte(fake_parser_chunked):
    fake_parser_chunked.incoming_data.extend(b'')
    for idx, val in enumerate(fake_parser_chunked._extract()):
        assert False
    assert isinstance(fake_parser_chunked.incoming_data, bytearray)
    assert fake_parser_chunked.incoming_data == b''


def test_chunk_no_separator(fake_parser_chunked):
    fake_parser_chunked.incoming_data.extend(b'abc')
    for idx, val in enumerate(fake_parser_chunked._extract()):
        assert False
    assert isinstance(fake_parser_chunked.incoming_data, bytearray)
    assert fake_parser_chunked.incoming_data == b'abc'


def test_process(fake_parser_chunked):
    i = 0
    for idx, val in enumerate(fake_parser_chunked.process(b'abc\ndef\ngh')):
        if i == 0:
            assert val == {'inp': b'abc'}
        elif i == 1:
            assert val == {'inp': b'def'}
        i += 1
    assert fake_parser_chunked.incoming_data == b'gh'

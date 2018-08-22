from unittest.mock import Mock

import pytest

from batterytester.components.sensor.incoming_parser.squid_parser import (
    SquidParser
)
from batterytester.core.helpers.helpers import FatalTestFailException


@pytest.fixture
def squid_parser():
    squid_parser = SquidParser(None, None, None)

    squid_parser.sensor_queue = Mock()
    squid_parser.sensor_queue.put_nowait = Mock()
    # squid_parser.finalize = Mock()
    return squid_parser


def test_chopper_full_chunk(squid_parser):
    incoming = b"{i:v:2.0}"
    squid_parser.chop(incoming)
    squid_parser.sensor_queue.put_nowait.assert_called_with(
        [b"i", b"v", b"2.0"]
    )
    assert squid_parser.sensor_queue.put_nowait.call_count == 1


def test_chopper(squid_parser):
    incoming = b"{i:v:2.0}"
    squid_parser.chop(incoming)
    squid_parser.sensor_queue.put_nowait.assert_called_with(
        [b"i", b"v", b"2.0"]
    )
    assert squid_parser.sensor_queue.put_nowait.call_count == 1

    incoming = b"{i2:v:3.0}"
    squid_parser.chop(incoming)
    squid_parser.sensor_queue.put_nowait.assert_called_with(
        [b"i2", b"v", b"3.0"]
    )
    assert squid_parser.sensor_queue.put_nowait.call_count == 2

    incoming = b"{s"
    squid_parser.chop(incoming)
    assert squid_parser.sensor_queue.put_nowait.call_count == 2

    incoming = b":s:s"
    squid_parser.chop(incoming)
    assert squid_parser.sensor_queue.put_nowait.call_count == 2

    incoming = b"}"
    squid_parser.chop(incoming)
    squid_parser.sensor_queue.put_nowait.assert_called_with([b"s", b"s", b"s"])
    assert squid_parser.sensor_queue.put_nowait.call_count == 3

    incoming = b"{}"
    with pytest.raises(FatalTestFailException):

        squid_parser.chop(incoming)

    incoming = b"{s:2}"
    with pytest.raises(FatalTestFailException):
        # todo: make this a dedicated exception ?
        squid_parser.chop(incoming)

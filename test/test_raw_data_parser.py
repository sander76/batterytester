from unittest.mock import Mock

import pytest

from batterytester.components.sensor.incoming_parser.squid_parser import (
    DictParser,
)
from batterytester.core.helpers.constants import ATTR_VALUES, ATTR_SENSOR_NAME

SENSOR_PREFIX = "abc"


@pytest.fixture
def dict_parser():
    sensor_queue = Mock()
    sensor_queue.put_nowait = Mock()

    dict_parser = DictParser(None, sensor_queue, SENSOR_PREFIX)

    return dict_parser


def test_dict_parser_prefix():
    parser = DictParser(None, None, "abc/abc")
    assert parser.sensor_prefix == "abc-abc"


def test_dict_parser(dict_parser):
    dict_parser.current_measurement = [b"i", b"v", b"12"]
    dict_parser.finalize()
    val = dict_parser.sensor_queue.put_nowait.call_args[0][0]

    assert val[ATTR_VALUES] == {"v": {"v": "12"}}
    assert val[ATTR_SENSOR_NAME] == SENSOR_PREFIX
    #
    dict_parser.current_measurement = [b"i", b"v", b"12", b"a", b"10"]
    dict_parser.finalize()
    val = dict_parser.sensor_queue.put_nowait.call_args[0][0]

    assert val[ATTR_VALUES] == {"v": {"v": "12", "a": "10"}}

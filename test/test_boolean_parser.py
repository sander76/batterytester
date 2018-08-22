from unittest.mock import Mock

import pytest

from batterytester.components.sensor.incoming_parser.boolean_parser import (
    BooleanParser
)
from batterytester.core.helpers.constants import (
    KEY_SUBJECT,
    ATTR_TIMESTAMP,
    ATTR_VALUES,
    ATTR_SENSOR_NAME,
)


@pytest.fixture
def fake_binary_parser():
    def _parser(sensor_prefix=None):
        sensor_queue = Mock()
        sensor_queue.put_nowait = Mock()
        parser = BooleanParser(None, sensor_queue, sensor_prefix=sensor_prefix)
        return parser

    return _parser


def test_finalize(fake_binary_parser):
    fake1 = fake_binary_parser()
    fake1.current_measurement = [b"s", b"7", b"1"]
    fake1.finalize()

    val = fake1.sensor_queue.put_nowait.call_args[0][0]
    assert val[ATTR_SENSOR_NAME] == "7"
    assert val[ATTR_VALUES] == {"v": True}
    assert KEY_SUBJECT in val
    assert ATTR_TIMESTAMP in val

    fake2 = fake_binary_parser()
    fake2.current_measurement = [b"s", b"7", b"0"]
    fake2.finalize()
    val = fake2.sensor_queue.put_nowait.call_args[0][0]
    assert val[ATTR_SENSOR_NAME] == "7"
    assert val[ATTR_VALUES] == {"v": False}


# def test_false_interpret(fake_binary_parser):
#     with pytest.raises(FatalTestFailException):
#         fake_binary_parser._interpret(b"abvf")


def test_sensor_name(fake_binary_parser):
    fake1 = fake_binary_parser("test_sensor")
    fake1.current_measurement = [b"s", b"7", b"0"]
    fake1.finalize()
    val = fake1.sensor_queue.put_nowait.call_args[0][0]

    assert val[ATTR_SENSOR_NAME] == "test-sensor_7"

    fake1.current_measurement = [b"s", b"def", b"0"]
    fake1.finalize()
    val = fake1.sensor_queue.put_nowait.call_args[0][0]

    assert val[ATTR_SENSOR_NAME] == "test-sensor_def"
    assert val[ATTR_VALUES] == {"v": False}

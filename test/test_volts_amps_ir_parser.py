from unittest.mock import Mock

import pytest

from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import (
    VoltAmpsIrParser
)
from batterytester.core.helpers.constants import (
    KEY_SUBJECT,
    ATTR_TIMESTAMP,
    ATTR_SENSOR_NAME,
    ATTR_VALUES,
)
from batterytester.core.helpers.helpers import FatalTestFailException


# todo: finish these tests.


@pytest.fixture
def fake_volt_amps_parser():

    sensor_queue = Mock()
    sensor_queue.put_nowait = Mock()
    parser = VoltAmpsIrParser(None, sensor_queue, None)
    return parser


def test_finalize(fake_volt_amps_parser):
    fake_volt_amps_parser.current_measurement = [
        b"s",
        b"v",
        b"1.0",
        b"a",
        b"3.5",
    ]
    fake_volt_amps_parser.finalize()
    val = fake_volt_amps_parser.sensor_queue.put_nowait.call_args[0][0]

    assert val[ATTR_SENSOR_NAME] == "VI"
    assert val[ATTR_VALUES]["v"]["amps"] == 3.5
    assert val[ATTR_VALUES]["v"]["volts"] == 1.0
    assert KEY_SUBJECT in val
    assert ATTR_TIMESTAMP in val


def test_false_interpret(fake_volt_amps_parser):
    with pytest.raises(FatalTestFailException):
        fake_volt_amps_parser.current_measurement = [b's']
        fake_volt_amps_parser.finalize()

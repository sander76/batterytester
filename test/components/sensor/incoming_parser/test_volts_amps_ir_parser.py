import logging
import math
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
from components.sensor.incoming_parser import get_measurement
from components.sensor.incoming_parser.volt_amps_ir_parser import (
    DownSampledVoltsAmpsParser
)

logging.basicConfig(level=logging.DEBUG)


@pytest.fixture
def fake_volt_amps_parser():
    sensor_queue = Mock()
    sensor_queue.put_nowait = Mock()
    parser = VoltAmpsIrParser(None, sensor_queue, None)
    return parser


delta_v = 0.1
delta_a = 0.1
buffer = 3


@pytest.fixture
def d_sampled_v_a_parser():
    sensor_queue = Mock()
    sensor_queue.put_nowait = Mock()
    parser = DownSampledVoltsAmpsParser(
        None, sensor_queue, None, delta_v=delta_v, delta_a=delta_a, buffer=10
    )
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
        fake_volt_amps_parser.current_measurement = [b"s"]
        fake_volt_amps_parser.finalize()


def make_sensor_data(volt, amps):
    return {"volts": volt, "amps": amps}


def get_measurements(sensor_data):
    for data in sensor_data:
        yield get_measurement("name", data)


def test_downsampled_volts_amps_parser_simple(d_sampled_v_a_parser):
    sensor_data = [make_sensor_data(1.0, 1.0), make_sensor_data(1.0, 1.0)]

    for measurement in get_measurements(sensor_data):
        d_sampled_v_a_parser.add_to_queue(measurement)

    assert d_sampled_v_a_parser.sensor_queue.put_nowait.call_count == 1


def test_downsampled_volts_amps_parser_option1(d_sampled_v_a_parser):
    sensor_data = [
        make_sensor_data(1.001, 1.0),
        make_sensor_data(1.002, 1.0),
        make_sensor_data(1.003, 1.0),
        make_sensor_data(1.004, 1.0),
        make_sensor_data(1.005, 1.0),
        make_sensor_data(1.1, 1.0),
        make_sensor_data(1.2, 1.0),
        make_sensor_data(1.001, 1.0),
        make_sensor_data(1.002, 1.0),
        make_sensor_data(1.003, 1.0),
        make_sensor_data(1.004, 1.0),
        make_sensor_data(1.005, 1.0),
        make_sensor_data(1.006, 1.0),
        make_sensor_data(1.007, 1.0),
        make_sensor_data(1.007, 1.0),
        make_sensor_data(1.008, 1.0),
        make_sensor_data(1.009, 1.0),
        make_sensor_data(1.010, 1.0),
        make_sensor_data(1.011, 1.0),
        make_sensor_data(1.012, 1.0),
        make_sensor_data(1.013, 1.0),
        make_sensor_data(1.0, 2),
        make_sensor_data(1.001, 1.0),
        make_sensor_data(1.0, 1.0),
        make_sensor_data(1.0, 1.0),
    ]
    for measurement in get_measurements(sensor_data):
        d_sampled_v_a_parser.add_to_queue(measurement)

    assert d_sampled_v_a_parser.sensor_queue.put_nowait.call_count == 9
    cal0 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[0][0][0]
    cal1 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[1][0][0]
    cal2 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[2][0][0]
    cal3 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[3][0][0]
    cal4 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[4][0][0]
    cal5 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[5][0][0]
    cal6 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[6][0][0]
    cal7 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[7][0][0]
    cal8 = d_sampled_v_a_parser.sensor_queue.put_nowait.call_args_list[8][0][0]

    assert math.isclose(cal0["v"]["v"]["volts"], 1.001, abs_tol=0.001)
    assert math.isclose(cal1["v"]["v"]["volts"], 1.005, abs_tol=0.001)
    assert math.isclose(cal2["v"]["v"]["volts"], 1.1, abs_tol=0.001)
    assert math.isclose(cal3["v"]["v"]["volts"], 1.2, abs_tol=0.001)
    assert math.isclose(cal4["v"]["v"]["volts"], 1.001, abs_tol=0.001)
    assert math.isclose(cal5["v"]["v"]["volts"], 1.011, abs_tol=0.001)
    assert math.isclose(cal6["v"]["v"]["volts"], 1.013, abs_tol=0.001)
    assert math.isclose(cal7["v"]["v"]["volts"], 1.0, abs_tol=0.001)
    assert math.isclose(cal8["v"]["v"]["volts"], 1.001, abs_tol=0.001)

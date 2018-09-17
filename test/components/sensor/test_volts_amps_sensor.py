import asyncio
from unittest.mock import Mock

from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import (
    VoltAmpsIrParser
)
from batterytester.components.sensor.volts_amps_sensor import VoltsAmpsSensor
from batterytester.components.sensor.incoming_parser.volt_amps_ir_parser import (
    DownSampledVoltsAmpsParser
)


def test_setup(monkeypatch):
    """Test the sensor setup method and assert all object and methods are
    correct."""

    buffer = 100
    delta_v = 1.1
    delta_a = 0.05

    vs = VoltsAmpsSensor(
        serial_port="abc",
        sensor_prefix="pref",
        buffer=buffer,
        delta_v=delta_v,
        delta_a=delta_a,
    )

    # During the setup call a connect call to the serial port needs to be made
    _connect_mock = Mock()
    monkeypatch.setattr(
        "batterytester.components.sensor.connector.squid_connector.AltArduinoConnector._connect",
        _connect_mock,
    )

    fake_bus = Mock()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(vs.setup("fake_test", fake_bus))

    assert isinstance(vs._sensor_data_parser, DownSampledVoltsAmpsParser)
    assert _connect_mock.called
    assert vs.sensor_prefix == "pref"
    assert vs._sensor_data_parser.sensor_prefix == "pref"
    assert vs._sensor_data_parser.buffer == buffer
    assert vs._sensor_data_parser.delta_v == delta_v
    assert vs._sensor_data_parser.delta_a == delta_a

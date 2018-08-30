import asyncio
from unittest.mock import Mock


from batterytester.components.sensor.incoming_parser.boolean_parser import \
    BooleanParser
from batterytester.components.sensor.led_gate_sensor import LedGateSensor


def test_setup(monkeypatch):
    """Test the sensor setup method and assert all object and methods are
    correct."""

    vs = LedGateSensor(serial_port="abc", sensor_prefix="pref")

    # During the setup call a connect call to the serial port needs to be made
    _connect_mock = Mock()
    monkeypatch.setattr(
        "batterytester.components.sensor.connector.squid_connector.AltArduinoConnector._connect",
        _connect_mock,
    )

    fake_bus = Mock()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(vs.setup("fake_test", fake_bus))

    assert isinstance(vs._sensor_data_parser, BooleanParser)
    assert _connect_mock.called
    assert vs.sensor_prefix == "pref"
    assert vs._sensor_data_parser.sensor_prefix == "pref"

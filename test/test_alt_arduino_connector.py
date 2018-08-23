import pytest

from batterytester.components.sensor.connector.squid_connector import \
    AltArduinoConnector
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import SquidConnectException

#todo: read this: https://faradayrf.com/unit-testing-pyserial-code/

def test_alt_arduino_connector_fail():
    bus = Bus()
    con = AltArduinoConnector(bus=bus, serial_port="fake_port")
    with pytest.raises(SquidConnectException):
        con._connect()

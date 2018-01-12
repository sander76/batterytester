import batterytester.connector.async_serial_connector as sc
import pytest
from unittest.mock import MagicMock
from serial import Serial, SerialException
from batterytester.bus import Bus
import asyncio


@pytest.fixture
def bus():
    bus = Bus()
    return bus


@asyncio.coroutine
def get_value(connection):
    val = yield from connection.raw_sensor_data_queue.get()
    return val


def test_serial_incoming(monkeypatch, bus):
    """Teest incoming data"""
    monkeypatch.setattr(
        'batterytester.connector.async_serial_connector.Serial',
        MagicMock(Serial))

    con = sc.AsyncSerialConnector(bus, MagicMock(), 124, 1234)
    con.s.read.side_effect = (b'a', SerialException)
    con.s.in_waiting = 1

    loop = asyncio.get_event_loop()
    return_val = loop.create_task(get_value(con))
    loop.run_forever()
    res = return_val.result()
    assert res == b'a'


def test_stop_test_on_serial_error(monkeypatch, bus):
    """Raising a serial exception on the serial read command
    should stop the complete test."""
    monkeypatch.setattr(
        'batterytester.connector.async_serial_connector.Serial',
        MagicMock(Serial))

    con = sc.AsyncSerialConnector(bus, MagicMock(), 124, 1234)
    con.s.read.side_effect = SerialException
    con.s.in_waiting = 1

    bus._start_test()
    assert True

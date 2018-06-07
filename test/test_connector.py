import asyncio
from unittest.mock import MagicMock

import pytest
from serial import Serial, SerialException

import batterytester.components.sensor.connector.async_serial_connector as sc
from batterytester.core.bus import Bus


@pytest.fixture
def bus():
    bus = Bus()
    return bus


async def get_value(connection):
    val = await connection.raw_sensor_data_queue.get()
    return val


def test_serial_incoming(monkeypatch, bus):
    """Test incoming data"""
    monkeypatch.setattr(
        'batterytester.components.sensor.connector.async_serial_connector.Serial',
        MagicMock(Serial))

    con = sc.AsyncSerialConnector(bus, MagicMock(), 124, 1234)
    con.s.read.return_value = b'a'
    con.s.in_waiting = 1

    loop = asyncio.get_event_loop()
    # return_val = loop.create_task(get_value(con))
    val = loop.run_until_complete(get_value(con))
    # res = return_val.result()
    assert val == b'a'


# def test_stop_test_on_serial_error(monkeypatch, bus):
#     """Raising a serial exception on the serial read command
#     should stop the complete test."""
#     monkeypatch.setattr(
#         'batterytester.components.sensor.connector.async_serial_connector.Serial',
#         MagicMock(Serial))
#
#     con = sc.AsyncSerialConnector(bus, MagicMock(), 124, 1234)
#     con.s.read.side_effect = SerialException
#     con.s.in_waiting = 1
#
#     async def fake_test():
#         pass
#
#     bus._start_test(fake_test(), 'fake_test')
#     assert True

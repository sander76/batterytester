import asyncio
from unittest.mock import Mock

import pytest

from batterytester.components.sensor.connector.arduino_connector import \
    ArduinoConnector
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import FatalTestFailException


def test_listen_for_data_raises():
    loop = asyncio.get_event_loop()
    bus = Bus(loop)

    connector = ArduinoConnector(
        bus=bus, serial_port=123, serial_speed=115200)

    def raiser():
        raise FatalTestFailException('test exception')

    connector._listen_for_data = raiser

    async def listen():
        await connector.async_listen_for_data()

    with pytest.raises(FatalTestFailException):
        loop.run_until_complete(listen())


def test_check_command():
    ac = ArduinoConnector(bus=Mock(), serial_port=10, serial_speed=115200)

    incoming = b'{s:v:22.33:a:222.4}\n'
    ac.check_command(incoming)
    args = ac.bus.loop.call_soon_threadsafe.call_args
    assert args[0][1] == b'v:22.33:a:222.4'

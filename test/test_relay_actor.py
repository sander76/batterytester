import asyncio
from unittest.mock import MagicMock, Mock

import pytest

import batterytester.core.actors.relay_actor as rl
from batterytester.core.actors.relay_actor import to_protocol

MOCK_SERIAL_PORT = 'abc'


@pytest.fixture
def fake_relay_actor(monkeypatch):
    fake_pv = rl.RelayActor(MOCK_SERIAL_PORT)

    return fake_pv


# @mock.patch("batterytester.core.actors.relay_actor.Serial", autospec=True)
def test_instantiate(monkeypatch, fake_relay_actor):
    fake_serial = MagicMock()
    write_mock = Mock()
    fake_serial.write = write_mock
    # fake_serial.__init__ = Mock()
    monkeypatch.setattr("batterytester.core.actors.relay_actor.Serial",
                        fake_serial)

    async def setup():
        await fake_relay_actor.setup(None, None)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(setup())
    fake_serial.assert_called_once_with(port=MOCK_SERIAL_PORT,
                                        baudrate=fake_relay_actor._speed)

    async def activate():
        await fake_relay_actor.activate(pin=2)

    loop.run_until_complete(activate())
    fake_relay_actor._serial.write.assert_called_once_with(
        'a:2:1\n'.encode('utf-8'))


def test_to_protocol():
    _ref = "a:2:3\n"
    _val = to_protocol('a', 2, 3)
    assert _ref == _val

    _val = to_protocol('a', 3, 2)
    assert _ref != _val

    _ref = "a:2\n"
    _val = to_protocol('a', 2)
    assert _ref == _val

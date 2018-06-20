from collections import OrderedDict
from unittest.mock import Mock

import pytest

from batterytester.components.datahandlers import Telegram
from batterytester.components.datahandlers.telegram import clean_for_markdown
from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import ActorResponse, AtomResult
from test.private_keys import telegram_token, telegram_sander


@pytest.fixture
def tg():
    _tg = Telegram(token='abc', chat_id='fake')
    _tg._send_message = Mock()
    return _tg


@pytest.fixture
def response(fake_time_stamp):
    resp = ActorResponse(OrderedDict([('t_est', 123), ('test1', 456)]))
    resp.time = fake_time_stamp
    return resp


def test_telegram_response_received(tg, response):
    _message = '*None*\n\nt est: 123\ntest1: 456\n22:33:09, Nov 29, 1973 '
    tg._actor_response_received('nosubj', response)

    tg._send_message.assert_called_once_with(_message)


def test_clean_for_markdown():
    _text = '_abc * `'
    _new = ' abc    '
    _val = clean_for_markdown(_text)
    assert _new == _val


def test_telegram_atom_result_received(tg):
    """Check if only failed tests are communicated."""
    _res = AtomResult(passed=False,
                      reason="Failed to communicate with PowerView hub: Cannot connect to host 192.168.1.11:80 ssl:None [Connect call failed ('192.168.1.11', 80)]")

    tg._atom_result('nosubj', _res)

    _res = AtomResult(passed=True,
                      reason='unknown')
    tg._atom_result('nosubj', _res)

    assert len(tg._send_message.mock_calls) == 1


def test_message_quality():
    telegram = Telegram(token=telegram_token, chat_id=telegram_sander)
    bus = Bus()

    # def add_task(coro):
    #     return coro

    # bus.add_async_task = add_task

    async def test_setup():
        await telegram.setup('this is a test', bus)

    def test_send(message):
        _res = AtomResult(passed=False, reason=message)
        telegram._atom_result('nosubj', _res)

    messages = [
        "Failed to communicate with PowerView hub: Cannot connect to host 192.168.1.11:80 ssl:None [Connect call failed ('192.168.1.11', 80)]",
    ]

    async def do_test():
        await test_setup()
        for message in messages:
            test_send(message)
            await bus.tasks[0]
            bus.tasks = []

    bus.loop.run_until_complete(do_test())
    pass

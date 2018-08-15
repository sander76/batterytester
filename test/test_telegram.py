from collections import OrderedDict
from unittest.mock import Mock

import pytest

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers import Telegram
from batterytester.components.datahandlers.telegram import clean_for_markdown
from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import (
    ActorResponse,
    AtomResult,
    FatalData,
)
from test.private_keys import telegram_token, chat_id


@pytest.fixture
def tg():
    _tg = Telegram(token="abc", chat_id="fake")
    _tg._send_message = Mock()
    return _tg


@pytest.fixture
def response(fake_time_stamp):
    resp = ActorResponse(OrderedDict([("t_est", 123), ("test1", 456)]))
    resp.time = fake_time_stamp
    return resp


@pytest.fixture
def fatal_data(fake_time_stamp):
    ft = FatalData("fatal reason unknown.")
    ft.time = fake_time_stamp
    ft.time_finished = fake_time_stamp
    return ft


def test_telegram_response_received(tg, response):
    _message = "*None*\n\n```\nt est: 123\ntest1: 456\n```\n\n22:33:09, Nov 29, 1973 "
    tg._actor_response_received("nosubj", response)

    tg._send_message.assert_called_once_with(_message)


def test_telegram_test_fata(tg, fatal_data):
    _message = "*None*\n\n```\nfatal reason unknown.\n```\n\n22:33:09, Nov 29, 1973 "
    tg._test_fatal("nosubj", fatal_data)
    tg._send_message.assert_called_once_with(_message)


def test_clean_for_markdown():
    _text = "_abc * `"
    _new = " abc    "
    _val = clean_for_markdown(_text)
    assert _new == _val


def test_telegram_atom_result_received(tg):
    """Check if only failed tests are communicated."""
    _res = AtomResult(
        passed=False,
        reason="Failed to communicate with PowerView hub: Cannot connect to host 192.168.1.11:80 ssl:None [Connect call failed ('192.168.1.11', 80)]",
    )

    tg._atom_result("nosubj", _res)

    _res = AtomResult(passed=True, reason="unknown")
    tg._atom_result("nosubj", _res)

    assert len(tg._send_message.mock_calls) == 1


def test_message_quality():
    telegram = Telegram(token=telegram_token, chat_id=chat_id)
    bus = Bus()

    async def test_setup():
        await telegram.setup("this is a test", bus)

    def test_send():
        _res = AtomResult(
            passed=False,
            reason="Failed to communicate with PowerView hub: Cannot connect to host 192.168.1.11:80 ssl:None [Connect call failed ('192.168.1.11', 80)]",
        )
        telegram._atom_result("nosubj", _res)

        _dct = OrderedDict([("key_1", "A very long message"), ("key_2", 1234)])
        _response = ActorResponse(_dct)
        telegram._actor_response_received("nosubj", _response)

    async def do_test():
        await test_setup()
        test_send()
        for task in bus.tasks:
            await task
        bus.tasks = []
        await bus.stop_test()

    bus.loop.run_until_complete(do_test())
    pass


def test_subscriptions():
    inf = Telegram(token=123, chat_id=123)

    subs = inf.get_subscriptions()

    assert len(subs) == len(inf.subscriptions)
    for sub in subs:
        assert sub in inf.subscriptions

    inf = Telegram(
        token=123,
        chat_id=123,
        subscription_filters=[subj.ACTOR_RESPONSE_RECEIVED],
    )
    subs = [sub for sub in inf.get_subscriptions()]
    assert len(subs) == 1
    assert subs[0][0] == subj.ACTOR_RESPONSE_RECEIVED

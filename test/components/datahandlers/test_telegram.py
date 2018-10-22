from collections import OrderedDict
from unittest.mock import Mock

import pytest

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.telegram import (
    clean_for_markdown,
    Telegram,
)
from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import (
    ActorResponse,
    AtomResult,
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


def test_telegram_response_received(tg, response):
    _message = (
        "*None*\n\n```\nt est: 123\ntest1: 456\n```\n\n22:33:09, Nov 29, 1973 "
    )
    tg.handle_event(subj.ACTOR_RESPONSE_RECEIVED, response)

    tg._send_message.assert_called_once_with(_message)


def test_telegram_test_data(tg, fatal_data):
    _message = "*None*\n\n```\nFATAL: fatal reason unknown.\n```\n\n22:33:09, Nov 29, 1973 "
    tg.handle_event(subj.TEST_FATAL, fatal_data)

    tg._send_message.assert_called_once_with(_message)


def test_event_test_warmup(tg, test_warmup_data):
    tg.handle_event(subj.TEST_WARMUP, test_warmup_data)
    assert tg._send_message.call_count == 1


def test_clean_for_markdown():
    _text = "_abc * `"
    _new = " abc    "
    _val = clean_for_markdown(_text)
    assert _new == _val


def test_event_atom_result(tg):
    """Check if only failed tests are communicated."""
    _res = AtomResult(
        passed=False,
        reason="Failed to communicate with PowerView hub: Cannot connect to host 192.168.1.11:80 ssl:None [Connect call failed ('192.168.1.11', 80)]",
    )

    tg.handle_event(subj.ATOM_RESULT, _res)
    _res = AtomResult(passed=True, reason="unknown")

    tg.handle_event(subj.ATOM_RESULT, _res)

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
        telegram.handle_event(subj.ATOM_RESULT, _res)

        _dct = OrderedDict([("key_1", "A very long message"), ("key_2", 1234)])
        _response = ActorResponse(_dct)
        telegram.handle_event(subj.ACTOR_RESPONSE_RECEIVED, _response)

    async def do_test():
        await test_setup()
        test_send()
        for task in bus.tasks:
            await task
        bus.tasks = []
        await bus.shutdown_test()

    bus.loop.run_until_complete(do_test())
    pass

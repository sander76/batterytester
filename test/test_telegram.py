from unittest.mock import Mock

import pytest

from batterytester.components.datahandlers import Telegram
from batterytester.components.datahandlers.telegram import clean_for_markdown
from batterytester.core.helpers.message_data import ActorResponse


@pytest.fixture
def tg():
    _tg = Telegram(token='abc', chat_id='fake')
    _tg._send_message = Mock()
    return _tg


@pytest.fixture
def response(fake_time_stamp):
    resp = ActorResponse({'t_est': 123, 'test1': 456})
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

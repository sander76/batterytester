"""Telegram. Notifies status updates on Telegram"""
import logging
import re
from asyncio import CancelledError
from datetime import datetime

from aiotg import Bot, BotApiError

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import \
    BaseDataHandler
from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import TestData, TestFinished, \
    ActorResponse, AtomResult

LOGGER = logging.getLogger(__name__)

replace = re.compile('[_*`]')


def clean_for_markdown(string):
    _new = re.sub(replace, ' ', string)
    return _new


class Telegram(BaseDataHandler):
    def __init__(self, *, token, chat_id):
        super().__init__()
        self._token = token
        self._chat_id = chat_id
        self._bus = None
        self._test_name = None
        self.bot = None

    async def setup(self, test_name: str, bus: Bus):
        self._bus = bus
        self._test_name = clean_for_markdown(test_name)
        self.bot = Bot(self._token)

    async def shutdown(self, bus: Bus):

        if self.bot.session:
            await self.bot.session.close()

    def get_subscriptions(self):
        return (
            (subj.TEST_WARMUP, self._test_start),
            (subj.TEST_FINISHED, self._test_finished),
            (subj.ACTOR_RESPONSE_RECEIVED, self._actor_response_received),
            (subj.ATOM_RESULT, self._atom_result)
        )

    def _to_time(self, value: int):
        return '{}'.format((datetime.fromtimestamp(value)).strftime(
            "%H:%M:%S, %b %d, %Y ")
        )

    def _atom_result(self, subject, data: AtomResult):
        """Handle atom result data"""

        if not data.passed.value:
            _info = data.reason.value
            self._send_message(self._make_message(_info, data.time.value))

    def _test_start(self, subject, data: TestData):
        _message = "*{}*\n\n{}\n{}".format(
            self._test_name,
            'STARTED',
            self._to_time(data.started.value)
        )

        self._send_message(_message)

    def _make_message(self, info, time):

        _message = "*{}*\n\n{}\n{}".format(
            self.test_name,
            clean_for_markdown(info),
            self._to_time(time)
        )
        return _message

    def _actor_response_received(self, subject, data: ActorResponse):
        _resp = '\n'.join("{}: {}".format(key, value) for key, value in
                          data.response.value.items())
        self._send_message(self._make_message(_resp, data.time.value))

    def _test_finished(self, subject, data: TestFinished):
        _message = "*{}*\n\n{}\n{}".format(
            self._test_name,
            'FINISHED',
            self._to_time(data.time_finished.value)
        )
        self._send_message(_message)

    def _send_message(self, message, parse_mode='Markdown'):
        async def send():
            try:
                await self.bot.send_message(
                    self._chat_id, message, parse_mode=parse_mode)
            except CancelledError:
                LOGGER.warning('send message task cancelled')
            except BotApiError as err:
                LOGGER.error(err)

        self._bus.add_async_task(send())

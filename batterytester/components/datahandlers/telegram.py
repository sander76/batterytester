"""Telegram. Notifies status updates on Telegram"""
import asyncio
import logging
import re
from asyncio import CancelledError
from datetime import datetime

from aiotg import Bot, BotApiError

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import (
    BaseDataHandler
)
from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import (
    TestData,
    TestFinished,
    ActorResponse,
    AtomResult,
    FatalData,
)

LOGGER = logging.getLogger(__name__)

replace = re.compile("[_*`]")


def clean_for_markdown(string):
    try:
        _new = re.sub(replace, " ", string)
        return _new
    except TypeError:
        return ""


class Telegram(BaseDataHandler):
    def __init__(self, *, token, chat_id, subscription_filters=None):
        super().__init__(subscription_filters=subscription_filters)
        self._token = token
        self._chat_id = chat_id
        self._bus = None
        self._test_name = None
        self.bot = None
        self.sending = False

        self.subscriptions = (
            (subj.TEST_WARMUP, self._test_start),
            (subj.TEST_FINISHED, self._test_finished),
            (subj.ACTOR_RESPONSE_RECEIVED, self._actor_response_received),
            (subj.ATOM_RESULT, self._atom_result),
            (subj.TEST_FATAL, self._test_fatal),
        )

    async def setup(self, test_name: str, bus: Bus):
        self._bus = bus
        self._test_name = clean_for_markdown(test_name)
        self.bot = Bot(self._token)

    async def shutdown(self, bus: Bus):
        LOGGER.info("Shutting down telegram.")
        tries = 10
        current_try = 0
        while current_try < tries:
            if self.sending:
                await asyncio.sleep(1)
            else:
                break
            current_try += 1
        if self.bot.session:
            await self.bot.session.close()

    @staticmethod
    def _to_time(value: int):
        return "{}".format(
            (datetime.fromtimestamp(value)).strftime("%H:%M:%S, %b %d, %Y ")
        )

    def _atom_result(self, subject, data: AtomResult):
        """Handle atom result data"""

        if not data.passed.value:
            _info = data.reason.value
            self._send_message(self._make_message(_info, data.time.value))

    def _test_start(self, subject, data: TestData):
        _message = self._make_message("STARTED", data.started.value)

        self._send_message(_message)

    def _make_message(self, info, time):

        _message = "*{}*\n\n```\n{}\n```\n\n{}".format(
            self.test_name, clean_for_markdown(info), Telegram._to_time(time)
        )
        return _message

    def _actor_response_received(self, subject, data: ActorResponse):
        _resp = "\n".join(
            "{}: {}".format(key, value)
            for key, value in data.response.value.items()
        )
        self._send_message(self._make_message(_resp, data.time.value))

    def _test_fatal(self, subject, data: FatalData):
        _info = data.reason.value
        self._send_message(self._make_message(_info, data.time_finished.value))

    def _test_finished(self, subject, data: TestFinished):
        _message = self._make_message("FINISHED", data.time_finished.value)

        self._send_message(_message)

    def _send_message(self, message, parse_mode="Markdown"):
        async def send():
            LOGGER.info("Sending telegram message.")
            try:
                self.sending = True
                await self.bot.send_message(
                    self._chat_id, message, parse_mode=parse_mode
                )
            except CancelledError:
                LOGGER.warning("send message task cancelled")
            except BotApiError as err:
                LOGGER.error(err)
            finally:
                self.sending = False

        self._bus.add_async_task(send())

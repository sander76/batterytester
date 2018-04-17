"""Telegram. Notifies status updates on Telegram"""
from datetime import datetime

from telepot.aio import Bot

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import \
    BaseDataHandler
from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import TestData, TestFinished


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
        self._test_name = test_name
        self.bot = Bot(self._token, self._bus.loop)

        # self.slack = SlackAPI(token=self._token, session=self._session)

    async def shutdown(self, bus: Bus):
        pass
        # self.slack.close()
        # if self._session:
        #     await self._session.close()

    def get_subscriptions(self):
        return (
            (subj.TEST_WARMUP, self._test_start),
            (subj.TEST_FINISHED, self._test_finished),
        )

    def _to_time(self, value: int):
        return '{}'.format((datetime.fromtimestamp(value)).strftime(
            "%H:%M:%S, %b %d, %Y ")
        )

    def _test_start(self, subject, data: TestData):
        _message = "*{}*\n\n{}\n{}".format(
            self._test_name,
            'STARTED',
            self._to_time(data.started.value)
        )

        self._send_message(_message)

    def _test_finished(self, subject, data: TestFinished):
        _message = "*{}*\n\n{}\n{}".format(
            self._test_name,
            'FINISHED',
            self._to_time(data.time_finished.value)
        )
        self._send_message(_message)

    def _send_message(self, message):
        self._bus.add_async_task(
            self.bot.sendMessage(self._chat_id, message, parse_mode='Markdown')
        )

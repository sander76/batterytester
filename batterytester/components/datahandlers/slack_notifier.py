"""Slackbot. Notifies status updates on Slack"""
from datetime import datetime

import slack
from slack.io.aiohttp import SlackAPI

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import \
    BaseDataHandler
from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import TestData, TestFinished


class SlackNotifier(BaseDataHandler):
    def __init__(self, *, slack_token, slack_channel='#setup1'):
        super().__init__()
        self._token = slack_token
        self._channel = slack_channel
        self._session = None
        self.slack = None
        self._bus = None
        self._test_name = None

    async def setup(self, test_name: str, bus: Bus):
        self._bus = bus
        self._session = bus.session
        self._test_name = test_name
        self.slack = SlackAPI(token=self._token, session=self._session)

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

    def _prop(self, prop, value):
        _val = '*{}:* {}'.format(prop, value)
        return _val

    def _to_time(self, value: int):
        return (datetime.fromtimestamp(value)).strftime(
            "%b %d %Y %H:%M:%S"
        )

    def _test_start(self, subject, data: TestData):
        _info = '\n'.join((self._prop('status', data.status.value),
                           self._prop('started',
                                      self._to_time(data.started.value))))
        attachments = [
            {
                'color': '#36a64f',
                'title': self._test_name,
                'mrkdwn_in': ['text', 'pretext'],
                'text': _info
            }
        ]
        self._send_to_slack(attachment=attachments)

    def _test_finished(self, subject, data: TestFinished):
        _info = '\n'.join(
            (self._prop('status', data.status.value),
             self._prop('stopped', self._to_time(data.time_finished.value))))

        attachments = [
            {'color': '#36a64f',
             'title': self._test_name,
             'text': _info,
             'mrkwn_in': ['text', 'pretext']}
        ]
        self._send_to_slack(attachment=attachments)

    def _send_to_slack(self, message=None, attachment=None):
        self._bus.add_async_task(
            self.slack.query(slack.methods.CHAT_POST_MESSAGE,
                             data={'channel': self._channel,
                                   'text': message,
                                   'attachments': attachment},
                             ))

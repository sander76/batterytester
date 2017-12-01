import asyncio

from aiopvapi.helpers.aiorequest import PvApiConnectionError

from batterytester.helpers.helpers import TestFailException
from batterytester.helpers.powerview_utils import PowerView
from batterytester.main_test import BaseTest


class PowerViewCustomCommandsReferenceTest(BaseTest):
    def __init__(
            self, test_name: str, loop_count: int,
            hub_ip: str,
            test_location: str = None,
            telegram_token=None, telegram_chat_id=None):
        super().__init__(
            test_name,
            loop_count,
            test_location,
            telegram_token,
            telegram_chat_id)
        self.powerview = PowerView(hub_ip, self.bus.loop, self.bus.session)

    @asyncio.coroutine
    def test_warmup(self):
        try:
            yield from self.powerview.get_shades()
            yield from self.powerview.get_scenes()
        except PvApiConnectionError:
            raise TestFailException("Failed to warmup the test.")

    def get_sequence(self):
        return self.custom_sequence(self)

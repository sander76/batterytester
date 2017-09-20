import asyncio

from batterytester.bus import Bus
from batterytester.helpers.helpers import get_current_time


class BaseConfig:
    """Base class for a test configuration"""

    def __init__(self):
        self.bus = Bus()
        self.loop_count = 1
        self.test_name = 'test_name'
        self.test_location = ''

    @asyncio.coroutine
    def test_warmup(self):
        """Gets called at the very start of a test"""
        pass

    @asyncio.coroutine
    def loop_warmup(self):
        """Gets called when a new loop is started."""
        pass

    def get_sequence(self):
        """Gets called to retrieve a list of test atoms to be performed.

        Must return a sequence of test atoms."""
        pass

    def start_test(self, add_time_stamp_to_report=True):
        if add_time_stamp_to_report:
            self.test_location = str(
                int(get_current_time().timestamp())) + '_' + self.test_location

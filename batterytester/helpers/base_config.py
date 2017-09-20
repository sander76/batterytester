import asyncio

from batterytester.bus import Bus
from batterytester.helpers.helpers import check_output_location
from batterytester.main_test.loop_test import LoopTest


class BaseConfig:
    """Base class for a test configuration"""

    def __init__(self):
        self.bus = Bus()
        self.loopcount = 1
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

    def start_test(self):
        pass


class LoopTestConfig(BaseConfig):
    def __init__(self):
        super().__init__()

    def start_test(self):
        if check_output_location(self.test_location):
            sequence_test = LoopTest(self)
            sequence_test.bus.start_test()

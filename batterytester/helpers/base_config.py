import asyncio

from batterytester.bus import Bus


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
        """Gets called to retrieve a list of test atoms to be performed."""
        pass

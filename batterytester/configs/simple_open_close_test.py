import asyncio
from aiopvapi.powerview_tool import PowerViewCommands
from batterytester.helpers.base_config import LoopTestConfig
from batterytester.helpers.helpers import TestFailException
from batterytester.test_atom import TestAtom


class TestConfig(LoopTestConfig):
    def __init__(self):
        super().__init__()
        self.hub_ip = '192.168.2.4'
        self.test_name = 'simple test'
        self.test_location = 'test_results/simple_open_close_test'
        self.loop_count = 1000
        self.shade_ids = [['1', 18390]]
        self.shades = []
        self.powerview_commands = PowerViewCommands(self.hub_ip, self.bus.loop,
                                                    self.bus.session)

    @asyncio.coroutine
    def get_shades(self):
        for _shade in self.shade_ids:
            _shade = yield from self.powerview_commands.get_shade(_shade[1])
            if _shade:
                self.shades.append(_shade)
            else:
                raise TestFailException("Error getting shades")
            yield from asyncio.sleep(6)

    @asyncio.coroutine
    def move_shades(self, open=False):
        result = True
        for _shade in self.shades:
            if open:
                result = yield from _shade.open()
            else:
                result = yield from _shade.close()
            yield from asyncio.sleep(6)
        return result

    @asyncio.coroutine
    def test_warmup(self):
        yield from self.get_shades()

    def get_sequence(self):
        _val = (
            TestAtom('shades open', self.move_shades, {'open': True}, 80),
            TestAtom('shades close', self.move_shades, {'open': False}, 80)
        )
        return _val


if __name__ == "__main__":
    config = TestConfig()
    config.start_test()

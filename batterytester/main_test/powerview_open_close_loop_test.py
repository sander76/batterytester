import asyncio

from aiopvapi.powerview_tool import PowerViewCommands

from batterytester.bus import Bus, TelegramBus
from batterytester.helpers.helpers import TestFailException
from batterytester.main_test import BaseTest
from batterytester.test_atom import TestAtom


class PowerViewOpenCloseLoopTest(BaseTest):
    def __init__(self, test_name,
                 loop_count, delay, shade_ids, hub_ip, test_location=None,
                 telegram_token=None, chat_id=None):
        if telegram_token and chat_id:
            bus = TelegramBus(telegram_token, chat_id)
        else:
            bus = Bus()
        self.delay = delay
        super().__init__(test_name, loop_count, bus,
                         sensor_data_connector=None,
                         database=None,
                         report=None,
                         test_location=test_location

                         )
        self.hub_ip = hub_ip
        self.shade_ids = shade_ids
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
            TestAtom(name='shades open',
                     command=self.move_shades,
                     arguments={'open': True},
                     duration=self.delay),
            TestAtom('shades close', self.move_shades, {'open': False},
                     self.delay)
        )
        return _val

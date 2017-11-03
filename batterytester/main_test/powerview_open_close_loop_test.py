import asyncio

from aiopvapi.powerview_tool import PowerViewCommands

from batterytester.bus import Bus, TelegramBus
from batterytester.helpers.helpers import TestFailException
from batterytester.main_test.base_test import BaseTest
from batterytester.test_atom import TestAtom


class PowerViewOpenCloseLoopTest(BaseTest):
    """Executes PowerView open and close hub commands.

    :param test_name: Name of the test
    :param loop_count: The amount of loops this test should run.
    :param delay: Delay between each command [seconds]
    :param shade_ids: The shades part of the test.
    :param hub_ip: Ip address of the PowerView hub.
    :param test_location: The folder location where report data is stored.
    :param telegram_token: For notification a telegram token can be supplied.
    :param chat_id: The telegram chat id where the notifications should be sent to.

    Report is stored as markdown.
    Database is json data file.

    A typical config file looks like:

    .. code-block:: python

        from batterytester.main_test.powerview_open_close_loop_test import PowerViewOpenCloseLoopTest

        test = PowerViewOpenCloseLoopTest(
        test_name="normal test",
        loop_count=10,
        delay=80,
        shade_ids=[['1', 46232]],
        hub_ip='192.168.0.106',
        telegram_token=None,
        chat_id=None
        )

        if __name__=="__main__":
            test.start_test()

    """

    def __init__(self, test_name,
                 loop_count, delay, shade_ids, hub_ip, test_location=None,
                 telegram_token=None, chat_id=None,shade_delay=3):
        """Initializes the class"""
        self.delay = delay
        super().__init__(test_name, loop_count,
                         sensor_data_connector=None,
                         database=None,
                         report=None,
                         test_location=test_location,
                         telegram_token=telegram_token,
                         telegram_chat_id=chat_id

                         )
        self.hub_ip = hub_ip
        self.shade_ids = shade_ids
        self.shades = []
        self.shade_delay=shade_delay
        self.powerview_commands = PowerViewCommands(self.hub_ip, self.bus.loop,
                                                    self.bus.session)

    @asyncio.coroutine
    def _get_shades(self):
        for _shade_id in self.shade_ids:
            _shade = yield from self.powerview_commands.get_shade(_shade_id[1])
            if _shade:
                self.shades.append(_shade)
            else:
                raise TestFailException("Error getting shades")
            yield from asyncio.sleep(6)

    @asyncio.coroutine
    def _move_shades(self, open=False):
        result = True
        for _shade in self.shades:
            if open:
                result = yield from _shade.open()
            else:
                result = yield from _shade.close()
            yield from asyncio.sleep(self.shade_delay)
        return result

    @asyncio.coroutine
    def test_warmup(self):
        """actions performed on the test subject before a new test
        is started. Should raise an TestFailException when an error occurs.
        """
        yield from self._get_shades()

    def get_sequence(self):
        _val = (
            TestAtom(name='shades open',
                     command=self._move_shades,
                     arguments={'open': True},
                     duration=self.delay),
            TestAtom('shades close', self._move_shades, {'open': False},
                     self.delay)
        )
        return _val

"""PowerView open close loop test. Running shades in an open/close loop."""

import asyncio

from aiopvapi.powerview_tool import PowerViewCommands
from batterytester.helpers.helpers import TestFailException
from batterytester.main_test import BaseTest
from batterytester.test_atom import TestAtom


class PowerViewOpenCloseLoopTest(BaseTest):
    """Executes PowerView open and close hub commands in a sequence.
    Per Atom an array of shades is sent to their open and close position.
    Within that atom each shade command (open/close) is sent in sequence with
    a certain delay.

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
                 loop_count: int, delay: int, shade_ids, hub_ip,
                 test_location=None,
                 telegram_token=None, chat_id=None, shade_delay=3):
        """
        :param str test_name: Name of the test
        :param int loop_count: The amount of loops this test should run.
        :param int delay: Delay in seconds between each command
        :param list shade_ids: The shades part of the test.
        :param str hub_ip: Ip address of the PowerView hub.
        :param str test_location: The folder location where report data is stored. If None no test data is stored.
        :param str telegram_token: For notification a telegram token can be supplied.
        :param str chat_id: The telegram chat id where the notifications should be sent to.
        :param int shade_delay: Delay between firing individual shades.
        """
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
        self.shade_delay = shade_delay
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
            TestAtom('shades close',
                     command=self._move_shades,
                     arguments={'open': False},
                     duration=self.delay)
        )
        return _val

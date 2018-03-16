from aiopvapi.helpers.aiorequest import PvApiConnectionError
from aiopvapi.helpers.powerview_util import PowerViewUtil

from batterytester.core.bus import Bus
from batterytester.core.datahandlers.report import Report
from batterytester.core.helpers.helpers import FatalTestFailException

from batterytester.main_test import BaseTest


class PowerViewLoopTest(BaseTest):
    def __init__(self, test_name,
                 loop_count, delay, hub_ip):
        self.delay = delay

        bus = Bus(self.async_test)

        # create data handlers.
        # _database = Influx(bus, influx_host, influx_database, test_name)
        _report = Report(test_name)

        # executors.
        self.powerview = PowerViewUtil(hub_ip, bus.loop, bus.session)

        super().__init__(bus, test_name, loop_count, data_handlers=_report)

    async def test_warmup(self):
        try:
            await self.powerview.get_shades()
        except PvApiConnectionError:
            raise FatalTestFailException("Failed to warmup the test.")

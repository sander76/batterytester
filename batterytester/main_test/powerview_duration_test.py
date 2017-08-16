import asyncio
import json
import logging
from asyncio.futures import CancelledError

import aiohttp

from batterytester.main_test import BaseTest

lgr = logging.getLogger(__name__)


class PowerViewDurationTest(BaseTest):
    def __init__(self, sensor_data_connector=None,
                 database=None, shade_id=None, power_view_hub_ip=None,
                 command_delay=60):
        BaseTest.__init__(
            self, sensor_data_connector, database)
        self.shade_id = shade_id
        self.ip = power_view_hub_ip
        self.url = 'http://{}/api/shades/{}'.format(
            power_view_hub_ip, shade_id)
        self.close_data = json.dumps(
            {'shade': {'id': shade_id,
                       'positions': {'posKind1': 1,
                                     'position1': 0}}})
        self.open_data = json.dumps(
            {'shade': {'id': shade_id,
                       'positions': {'posKind1': 1,
                                     'position1': 65535}}})
        self.command_delay = command_delay
        self.ir = 0
        # self.bus.loop.create_task(self.cycle_up_down())

    def handle_sensor_data(self, sensor_data):
        _ir = sensor_data.get('ir')
        if _ir:
            self.ir = _ir

    @asyncio.coroutine
    def _send_open(self):
        resp = yield from self.bus.session.put(self.url, data=self.open_data)
        assert resp.status == 200
        yield from resp.release()

    @asyncio.coroutine
    def send_open(self):
        lgr.debug("Sending open command to: {}".format(self.ip))
        yield from self._send_open()
        yield from asyncio.sleep(1)
        yield from self._send_open()
        yield from self.database.add_to_database({'open': 1})
        return True

    @asyncio.coroutine
    def _send_close(self):
        resp = yield from self.bus.session.put(self.url, data=self.close_data)
        assert resp.status == 200
        yield from resp.release()

    @asyncio.coroutine
    def send_close(self):
        lgr.debug("Sending close command to: {}".format(self.ip))
        yield from self._send_close()
        yield from asyncio.sleep(1)
        yield from self._send_close()
        yield from self.database.add_to_database({'close': 1})
        return True

    @asyncio.coroutine
    def init_test(self):
        lgr.debug("Initializing test.")
        yield from self.send_open()
        yield from asyncio.sleep(120)
        yield from self.send_close()
        yield from asyncio.sleep(120)

    @asyncio.coroutine
    def async_test(self):
        try:
            yield from self.init_test()
            try:
                lgr.debug("Starting actual test.")
                while self.bus.running:
                    if self.ir == 0:
                        yield from self.send_open()
                    else:
                        self.bus.stop_test(
                            "Ir sensor has value of one. "
                            "Should be zero. Breaking loop")
                    yield from asyncio.sleep(self.command_delay)
                    if self.ir == 1:
                        yield from self.send_close()
                    else:
                        self.bus.stop_test(
                            "Ir sensor has value of zero. "
                            "Should be one. Breaking loop.")
                    yield from asyncio.sleep(self.command_delay)
            except aiohttp.errors.ClientOSError:
                self.bus.stop_test("Cannot connect to PowerView hub.")
            except AssertionError as e:
                self.bus.stop_test(
                    "Something is wrong with the following "
                    "PowerView ip address: {}".format(self.url))
        except CancelledError:
            lgr.debug("stopping loop test")

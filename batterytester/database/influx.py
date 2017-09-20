import asyncio
import logging
from time import time
import aiohttp
import async_timeout

from batterytester.database import DataBase
from batterytester.helpers import Bus
LENGTH = 30

lgr = logging.getLogger(__name__)


# def setup(args):
#     return Influx(**args)


class Influx(DataBase):
    def __init__(
            self, bus: Bus, host=None, database=None,
            measurement=None, datalength=LENGTH):
        DataBase.__init__(self, bus)
        self.host = host
        self.data = []
        self.url = 'http://{}:8086/write?db={}&precision=ms'.format(host,
                                                                    database)
        self.measurement = measurement
        self.data_length = datalength

    # todo: move timestamp to the moment of datacollection.
    def _get_time_stamp(self):
        return int(time() * 1000)

    @asyncio.coroutine
    def add_to_database(self, *datapoints):
        for _data in datapoints:
            self.data.append(self._create_measurement(_data))
            yield from self._check_and_send_to_database()

    def _create_measurement(self, datapoint):
        _datapoint = self._add_data_points(datapoint)
        ts = self._get_time_stamp()
        ln = '{} {} {}'.format(self.measurement, _datapoint, ts)
        return ln

    def _add_data_points(self, datapoints: dict):
        lgr.debug("adding: {}".format(dict))
        _datapoints = ','.join("{}={}".format(key, value) for key, value in
                               datapoints.items())
        return _datapoints

    @asyncio.coroutine
    def _check_and_send_to_database(self):
        """Checks the length of the data and
        if long enough sends it to the database."""

        if len(self.data) > self.data_length:
            _data = self.prepare_data()
            # clear the list so asyncio can start populate
            # it while processing the next yields.
            self.data = []
            yield from self._send(_data)
        return

    def prepare_data(self):
        _data = '\n'.join(self.data)
        _data += '\n'
        return _data

    @asyncio.coroutine
    def _send(self, data):
        resp = None
        try:
            with async_timeout.timeout(5, loop=self.bus.loop):
                resp = yield from self.bus.session.post(self.url, data=data)
            if resp.status != 204:
                self.bus.stop_test(
                    "Wrong response code {}".format(resp.status))
        except (asyncio.TimeoutError, aiohttp.errors.ClientError,
                aiohttp.errors.ClientDisconnectedError) as err:
            lgr.exception(err)
            self.bus.stop_test("Problems writing data to database")
        finally:
            if resp is not None:
                yield from resp.release()
        return True
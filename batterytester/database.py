import asyncio
import logging
from time import time
import aiohttp
import async_timeout

from batterytester.helpers import get_bus

LENGTH = 30

lgr = logging.getLogger(__name__)


class DataBase:
    def __init__(
            self, host, database, measurement, datalength=LENGTH):
        self.host = host
        self.data = []
        self.url = 'http://{}:8086/write?db={}&precision=ms'.format(host,
                                                                    database)
        self.measurement = measurement
        self.data_length = datalength
        self.bus = get_bus()

    def _get_time_stamp(self):
        return int(time() * 1000)

    @asyncio.coroutine
    def add_to_database(self, *datapoints):
        for _data in datapoints:
            self.data.append(self.create_measurement(_data))
            yield from self.check_and_send_to_database()

    def create_measurement(self, datapoint):
        _datapoint = self._add_data_points(datapoint)
        ts = self._get_time_stamp()
        ln = '{} {} {}'.format(self.measurement, _datapoint, ts)
        return ln

    def _add_data_points(self, datapoints: dict):
        lgr.debug("adding: {}".format(dict))
        _datapoints = ','.join("{}={}".format(key, value) for key, value in
                               datapoints.items())
        return _datapoints

    # @asyncio.coroutine
    # def clean_milliamps(self, milliamps):
    #     if milliamps < 0:
    #         return 0
    #     elif milliamps > 0 and milliamps <= 0.5:
    #         return 0.5
    #     else:
    #         return round(milliamps)

    @asyncio.coroutine
    def check_and_send_to_database(self):
        """Checks the length of the data and
        if long enough sends it to the database."""

        if len(self.data) > self.data_length:
            _data = self.prepare_data()
            # clear the list so asyncio can start populate
            # it while processing the next yields.
            self.data = []
            yield from self.send(_data)
        return

    def prepare_data(self):
        _data = '\n'.join(self.data)
        _data += '\n'
        return _data

    @asyncio.coroutine
    def send(self, data):
        try:
            # todo add a timeout when posting takes too long. (?)
            resp = yield from self.bus.session.post(self.url, data=data)
            # except Exception as e:
            #     raise TestException("problems !")
            # 204 code from influx db means all is ok.
            assert resp.status == 204
            resp.release()

        except aiohttp.errors.ClientError as e:
            lgr.exception(e)
            self.bus.stop_test("Problems writing data to database")
        except aiohttp.errors.ClientOSError as e:
            lgr.exception(e)
            self.bus.stop_test("Problems writing data to database")
        except AssertionError as e:
            lgr.exception(e)
            self.bus.stop_test("Problems writing data to database")

        return True


if __name__ == "__main__":

    def add_data():
        for i in range(30):
            volt = 10.3 + i
            amps = 3.44 + i
            resp = yield from db.add_data(volt, amps)
            print(resp)


    import aiohttp

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    db = DataBase("192.168.0.113", "batterytest", "blind10", session,
                  datalength=3)
    # loop.create_task(add_data())
    loop.run_until_complete(add_data())

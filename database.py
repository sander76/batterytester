import asyncio
import logging
import aiohttp
from time import time

LENGTH = 10

lgr = logging.getLogger(__name__)


class DataBase:
    def __init__(self, host, database, measurement, session, loop, datalength=LENGTH):
        self.host = host
        self.data = []
        self.url = 'http://{}:8086/write?db={}&precision=ms'.format(host, database)
        self.measurement = measurement
        self.session = session
        self.data_length = datalength
        self.loop = loop

    def _get_time_stamp(self):
        return int(time() * 1000)

    #@asyncio.coroutine
    def add_ir_data(self, ir):
        lgr.debug("adding data: ir value: {}".format(ir))
        ts = self._get_time_stamp()
        ln = '{} ir={} {}'.format(self.measurement, ir, ts)
        self.data.append(ln)
        return

    @asyncio.coroutine
    def add_open(self):
        lgr.debug("adding open command")
        ts = self._get_time_stamp()
        ln = '{} open=1 {}'.format(self.measurement, ts)
        self.data.append(ln)

    @asyncio.coroutine
    def add_close(self):
        lgr.debug("adding close command")
        ts = self._get_time_stamp()
        ln = '{} close=1 {}'.format(self.measurement, ts)
        self.data.append(ln)

    #@asyncio.coroutine
    def add_data(self, volts, milliamps):
        lgr.debug("adding data: volts: {} amps: {}".format(volts, milliamps))
        ts = self._get_time_stamp()
        ln = '{} volts={},amps={} {}'.format(self.measurement, volts, milliamps, ts)
        self.data.append(ln)

    @asyncio.coroutine
    def clean_milliamps(self, milliamps):
        if milliamps < 0:
            return 0
        elif milliamps > 0 and milliamps <= 0.5:
            return 0.5
        else:
            return round(milliamps)

    @asyncio.coroutine
    def sender(self):
        '''
        Checks the length of the data and if long enough sends it to the database.
        :return:
        '''
        if len(self.data) > self.data_length:
            _data = self.prepare_data()
            # clear the list so asyncio can start populate it while processing the next yields.
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
            resp = yield from self.session.post(self.url, data=data)
            # 204 code from influx db means all is ok.
            assert resp.status == 204
            return
        except aiohttp.errors.ClientOSError as e:
            lgr.info("Problems writing data to database")
            self.loop.stop()
        except AssertionError as e:
            lgr.info("Response from influx db not correct response:")
            self.loop.stop()
        finally:
            yield from resp.release()
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
    db = DataBase("192.168.0.113", "batterytest", "blind10", session, datalength=3)
    # loop.create_task(add_data())
    loop.run_until_complete(add_data())

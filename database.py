import asyncio
import logging
from time import time

LENGTH = 10

lgr = logging.getLogger(__name__)

class DataBase:
    def __init__(self, host, database, measurement, session, datalength=LENGTH):
        self.host = host
        self.data = []
        self.url = 'http://{}:8086/write?db={}&precision=ms'.format(host, database)
        self.measurement = measurement
        self.session = session
        self.data_length = datalength

    @asyncio.coroutine
    def add_data(self, volts, amps):
        lgr.debug("adding data: volts: {} amps: {}".format(volts,amps))
        ts = int(time() * 1000)
        ln = '{} volts={},amps={} {}'.format(self.measurement, volts, amps, ts)
        self.data.append(ln)
        #if len(self.data) == self.data_length:
            # _data = self.prepare_data()
            # self.data = []
            # resp = yield from self.send(_data)
            # return resp
        return True


    @asyncio.coroutine
    def sender(self):
        '''
        Checks the length of the data and if long enough sends it to the database.
        :return:
        '''
        if len(self.data)==self.data_length:
            _data = self.prepare_data()
            # clear the list so asyncio can start populate it while processing the next yields.
            self.data = []
            resp = yield from self.send(_data)
            assert resp.status == 200
            yield from resp.release()
        return

    def prepare_data(self):
        _data = '\n'.join(self.data)
        _data += '\n'
        return _data

    @asyncio.coroutine
    def send(self, data):
        try:
            resp = yield from self.session.post(self.url, data=data)
            yield from resp.release()
        except aiohttp.errors.ClientOSError as e:
            raise UserWarning("Problems writing data to database")
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

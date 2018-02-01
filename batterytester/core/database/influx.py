import asyncio
import logging
from asyncio import CancelledError
from typing import Union

import async_timeout
from aiohttp.client_exceptions import ClientError

from batterytester.core.atom import Atom
from batterytester.core.bus import Bus
from batterytester.core.database import DataBase
from batterytester.core.helpers.constants import ATTR_VALUES, ATTR_TIMESTAMP
from batterytester.core.helpers.helpers import FatalTestFailException

LENGTH = 5

LOGGER = logging.getLogger(__name__)


def line_format_fields(measurement: dict):
    """Create the fields and their values."""
    return ','.join("{}={}".format(key, value) for key, value in
                    measurement.items() if
                    key != ATTR_TIMESTAMP)


def line_protocol_tags(atom: Atom):
    if atom:
        return ',idx={},loop={}'.format(atom.idx, atom.loop)
    return ''


# todo: write the buffer to the database when the test ends.
# todo: write tests.

class Influx(DataBase):
    def __init__(
            self, bus: Bus, host=None, database='menc',
            measurement=None, datalength=LENGTH):
        """

        :param bus:
        :param host:
        :param database: The database to write data to.
        :param measurement: The current test being run. normally the name of the test.
        :param datalength:
        """
        DataBase.__init__(self, bus)
        self.host = host
        self.data = []
        self.url = 'http://{}:8086/write?db={}&precision=ms'.format(
            host, database)
        self.measurement = measurement  # actually the name of the test.
        self.data_length = datalength
        self.bus.add_async_task(
            self._check_and_send_to_database())
        self.bus.add_closing_task(self._flush())

    @asyncio.coroutine
    def _add_to_database(self, datapoint, atom: Union[Atom, None]):

        self.data.append(self._create_measurement(datapoint, atom))

    def _create_measurement(self, measurement: dict, atom=None):
        """Transform data according to line format protocol.

        <measurement>[,<tag-key>=<tag-value>...] <field-key>=<field-value>[,<field2-key>=<field2-value>...] [unix-nano-timestamp]

test_name,loop=x,index=x temp=82 1465839830100400200
  |       -------------- -------        |
  |             |             |         |
  |             |             |         |
+-----------+--------+-+---------+-+---------+
|measurement|,tag_set| |field_set| |timestamp|
+-----------+--------+-+---------+-+---------+

        example:
        cpu,host=serverA,region=us_west value=0.64
        """
        ln = '{}{} {} {}'.format(
            self.measurement, line_protocol_tags(atom),
            line_format_fields(measurement), measurement.get(ATTR_TIMESTAMP))
        return ln

    @asyncio.coroutine
    def _check_and_send_to_database(self):
        """Checks the length of the data list and
        if long enough sends it to the database."""

        try:
            while self.bus.running:
                if len(self.data) > self.data_length:
                    LOGGER.debug("buffer limit exceeded. Flushing data")
                    yield from self._flush()
                else:
                    yield from asyncio.sleep(5)
        except CancelledError:
            LOGGER.info("Test cancelled. Closing database.")

        # Flush remaining data before loop is closed.
        # _data = self.prepare_data()
        # self.bus.add_closing_task(self._send(_data))
        return

    def prepare_data(self):
        if self.data:
            _data = '\n'.join(self.data)
            _data += '\n'
            return _data

    @asyncio.coroutine
    def _flush(self):
        _data = self.prepare_data()
        # clear the list so asyncio can start populating
        # it while processing the next yields.

        self.data = []
        if _data:
            yield from self._send(_data)

    @asyncio.coroutine
    def _send(self, data):
        resp = None
        try:
            LOGGER.debug("Flushing")
            with async_timeout.timeout(5, loop=self.bus.loop):
                LOGGER.debug("Sending data to database")
                resp = yield from self.bus.session.post(self.url, data=data)
            if resp.status != 204:
                self.bus.stop_test(
                    "Wrong response code {}".format(resp.status))
        except (asyncio.TimeoutError, ClientError) as err:
            LOGGER.error(err)
            raise FatalTestFailException("Error sending data to database")
        except asyncio.CancelledError:
            LOGGER.debug("sending to database cancelled.")

        finally:
            if resp is not None:
                yield from resp.release()

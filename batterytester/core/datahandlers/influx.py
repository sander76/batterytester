import asyncio
import logging
import async_timeout
import batterytester.core.helpers.message_subjects as subj

from asyncio import CancelledError
from slugify import slugify
from aiohttp.client_exceptions import ClientError
from batterytester.core.bus import Bus
from batterytester.core.datahandlers import BaseDataHandler
from batterytester.core.helpers.constants import ATTR_TIMESTAMP, KEY_ATOM_LOOP, \
    KEY_VALUE, KEY_ATOM_INDEX, KEY_ATOM_NAME, KEY_SUBJECT
from batterytester.core.helpers.helpers import FatalTestFailException
from batterytester.core.helpers.message_data import AtomData

LENGTH = 1

LOGGER = logging.getLogger(__name__)


def line_protocol_fields(measurement: dict):
    """Create the fields and their values.
    But remove the timestamp attribute

    incoming is a dict with {KEY:{KEY_VALUE:VALUE}} structure.
    """
    return ','.join("{}={}".format(key, value[KEY_VALUE]) for key, value in
                    measurement.items() if
                    key != ATTR_TIMESTAMP and key != KEY_SUBJECT)


def line_protocol_tags(tags: dict):
    """Create influx measurement tags.

    Incoming is dict with key:value pairs."""
    if tags:
        _val = ',{}'.format(','.join(
            ('{}={}'.format(key, value) for key, value in tags.items())))
        return _val
    # if atom:
    #     return ',idx={},loop={}'.format(atom.idx, atom.loop)
    return ''


def get_time_stamp(data):
    """Incoming is a float in seconds.

    Return value is a nanosecond integer."""
    val = data.get(ATTR_TIMESTAMP)
    if val:
        val = val.get(KEY_VALUE)
        return to_nano_seconds(val)  # to nanoseconds.
    else:
        raise FatalTestFailException("Data has no timestamp")


def to_nano_seconds(timestamp):
    """Milliseconds to nanoseconds"""

    try:
        val = int(timestamp * 1000000000)
        return val
    except Exception:
        raise FatalTestFailException(
            "Unable to convert milliseconds to nanoseconds.")


# todo: write the buffer to the database when the test ends.
# todo: write tests.

class Influx(BaseDataHandler):
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
        super().__init__()
        self.bus = bus
        self.host = host
        self.data = []
        # self.url = 'http://{}:8086/write?db={}&precision=ms'.format(
        #     host, database)
        self.url = 'http://{}:8086/write?db={}'.format(
            host, database)
        self.measurement = measurement  # actually the name of the test.
        self.data_length = datalength
        self.bus.add_async_task(
            self._check_and_send_to_database())
        self.bus.add_closing_task(self._flush())
        self._tags = {}

    def get_subscriptions(self):
        return (
            (subj.ATOM_WARMUP, self._store_tag_data),
            (subj.SENSOR_DATA, self._add_to_database),
        )

    def _store_tag_data(self, subject, data: AtomData):
        LOGGER.debug("storing tag data")
        self._tags['loop'] = data.loop.value  # data[KEY_ATOM_LOOP][KEY_VALUE]
        self._tags['idx'] = data.idx.value  # data[KEY_ATOM_INDEX][KEY_VALUE]

        _fields = line_protocol_fields({'value': {KEY_VALUE: 1}})
        _tags = {
            'name': slugify(data.atom_name.value),
            'loop': data.loop.value,
            'idx': data.idx.value
        }
        _tags = line_protocol_tags(_tags)
        self.data.append(self._create_measurement(
            _fields, _tags, to_nano_seconds(data.started.value)))

    def _add_to_database(self, subject, data):
        # LOGGER.debug("Adding to database buffer")
        _time_stamp = get_time_stamp(data)
        # if subject == subj.SENSOR_DATA:
        _fields = line_protocol_fields(data)
        _tags = line_protocol_tags(
            dict(self._tags))  # Shallow copy of the current tags.
        self.data.append(
            self._create_measurement(_fields, _tags, _time_stamp))
        # elif subject == subj.ATOM_WARMUP or subject == subj.ATOM_STATUS:
        #     _fields = line_protocol_fields({'value': {KEY_VALUE: 1}})
        #
        #     _tags = dict(self._tags)
        #     _tags['name'] = slugify(data.atom_name.value)
        #     _tags = line_protocol_tags(_tags)
        #
        #     self.data.append(
        #         self._create_measurement(_fields, _tags, _time_stamp))

    def _create_measurement(self, fields: str, tags: str, time_stamp):
        """Transform data according to line format protocol.

        <measurement>[,<tag-key>=<tag-value>...] <field-key>=<field-value>[,<field2-key>=<field2-value>...] [unix-nano-timestamp]

        test_name,loop=x,index=x temp=82 1465839830100400200
          |       -------------- -------        |
          |             |             |         |
          |             |             |         |
        +-----------+--------+-+---------+-+---------+
        |measurement|,tag_set| |field_set| |timestamp|
        +-----------+--------+-+---------+-+---------+

        """
        ln = '{}{} {} {}'.format(
            self.measurement, tags, fields, time_stamp)
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
                LOGGER.debug("Writing data to database")
                resp = yield from self.bus.session.post(self.url,
                                                        data=data)
            if resp.status not in [204, 200]:
                raise FatalTestFailException(
                    "Wrong influx response code {}".format(resp.status))
        except (asyncio.TimeoutError, ClientError) as err:
            LOGGER.error(err)
            raise FatalTestFailException("Error sending data to database")
        finally:
            if resp is not None:
                yield from resp.release()

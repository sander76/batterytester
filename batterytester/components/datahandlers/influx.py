import asyncio
import logging

import async_timeout
from aiohttp.client_exceptions import ClientError
from slugify import slugify

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import \
    BaseDataHandler
from batterytester.core.bus import Bus
from batterytester.core.helpers.constants import ATTR_TIMESTAMP, KEY_VALUE, \
    ATTR_VALUES, ATTR_SENSOR_NAME
from batterytester.core.helpers.helpers import FatalTestFailException
from batterytester.core.helpers.message_data import AtomData

LOGGER = logging.getLogger(__name__)


class InfluxLineProtocol:
    """https://docs.influxdata.com/influxdb/v1.5/write_protocols/line_protocol_tutorial/"""

    def __init__(self, measurement, time_stamp, tags: dict = None,
                 fields: dict = None):
        """

        :param measurement:
        :param tags:
        :param fields:
        :param time_stamp: float in seconds.
        """
        self._measurement = slugify(measurement)
        self._tags = tags
        self._fields = fields
        self._timestamp = time_stamp

    def create_measurement(self):
        return ' '.join(self.creator())

    def creator(self):
        if self._tags:
            yield '{},{}'.format(self._measurement,
                                 line_protocol_fields(self._tags))
        else:
            yield self._measurement
        if self._fields:
            yield line_protocol_fields(self._fields)
        yield str(to_nanoseconds(self._timestamp))


def line_protocol_fields(tags: dict):
    """Create the fields and their values.

    incoming is a dict with {KEY_VALUE:VALUE} structure.
    """

    return ','.join(("{}={}".format(key, value) for key, value in
                     tags.items()))


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
        return to_nanoseconds(val)  # to nanoseconds.
    else:
        raise FatalTestFailException("Data has no timestamp")


def to_nanoseconds(timestamp):
    """Milliseconds to nanoseconds"""

    try:
        val = int(timestamp * 1000000000)
        return val
    except Exception as err:
        LOGGER.error(err)
        raise FatalTestFailException(
            "Unable to convert milliseconds to nanoseconds.")


# todo: write tests.

class Influx(BaseDataHandler):
    """Writes data to an InfluxDB database."""

    def __init__(
            self, *, host=None, database='menc', buffer_size=5):
        """
        :param host: ip address of the influx database
        :param database: The database to write data to.
        :param buffer_size: buffer length before call to influx api is made.
        """
        super().__init__()
        self.host = host
        self.data = []
        self.bus = None
        self.url = 'http://{}:8086/write?db={}'.format(
            host, database)
        self.measurement = None  # actually the name of the test.
        self.buffer_size = buffer_size
        self._tags = {}

    async def setup(self, test_name, bus):
        self.bus = bus
        self.measurement = test_name

    async def shutdown(self, bus: Bus):
        await self._flush()

    def get_subscriptions(self):
        return (
            (subj.ATOM_WARMUP, self._atom_warmup_event),
            (subj.SENSOR_DATA, self._handle_sensor)
        )

    def add_to_buffer(self, data: InfluxLineProtocol):
        """Add influx line data to buffer and check size"""
        self.data.append(data)
        if len(self.data) > self.buffer_size:
            self._flush()

    def _atom_warmup_event(self, subject, data: AtomData):
        self._tags['loop'] = data.loop.value  # data[KEY_ATOM_LOOP][KEY_VALUE]
        self._tags['idx'] = data.idx.value  # data[KEY_ATOM_INDEX][KEY_VALUE]

        annotation_tags = 'loop {},index {}'.format(data.loop.value, data.idx.value)
        _influx = InfluxLineProtocol(
            self.measurement,
            data.started.value,
            fields={'title': 'atom warmup',
                    'text': data.atom_name.value,
                    'tags': annotation_tags}
        )
        self.add_to_buffer(_influx)

    # def _store_tag_data(self, data: AtomData):
    #     LOGGER.debug("storing tag data")
    #     self._tags['loop'] = data.loop.value  # data[KEY_ATOM_LOOP][KEY_VALUE]
    #     self._tags['idx'] = data.idx.value  # data[KEY_ATOM_INDEX][KEY_VALUE]
    #
    #     _fields = line_protocol_fields({'value': {KEY_VALUE: 1}})
    #     _tags = {
    #         'name': slugify(data.atom_name.value),
    #         'loop': data.loop.value,
    #         'idx': data.idx.value
    #     }
    #     _tags = line_protocol_tags(_tags)
    #     self.data.append(self._create_measurement(
    #         _fields, _tags, to_nanoseconds(data.started.value)))
    #     self.check_buffer()

    def _handle_sensor(self, subject, data):
        influx = InfluxLineProtocol(
            self.measurement,
            data[ATTR_TIMESTAMP][ATTR_VALUES],
            tags=self._tags,
            fields={data[ATTR_SENSOR_NAME]: data[ATTR_VALUES][ATTR_VALUES]}
        )
        self.add_to_buffer(influx)

        # # LOGGER.debug("Adding to database buffer")
        # _time_stamp = get_time_stamp(data)
        # _fields = line_protocol_fields(data[ATTR_VALUES][ATTR_VALUES])
        #
        #
        #
        # self._tags[ATTR_SENSOR_NAME] = data[ATTR_SENSOR_NAME]
        # _tags = line_protocol_tags(self._tags)
        # self.data.append(
        #     self._create_measurement(_fields, _tags, _time_stamp))
        # self.check_buffer()

    # def _create_measurement(self, fields: str, tags: str, time_stamp):
    #     """Transform data according to line format protocol.
    #
    #     <measurement>[,<tag-key>=<tag-value>...] <field-key>=<field-value>[,<field2-key>=<field2-value>...] [unix-nano-timestamp]
    #
    #     test_name,loop=x,index=x temp=82 1465839830100400200
    #       |       -------------- -------        |
    #       |             |             |         |
    #       |             |             |         |
    #     +-----------+--------+-+---------+-+---------+
    #     |measurement|,tag_set| |field_set| |timestamp|
    #     +-----------+--------+-+---------+-+---------+
    #
    #     """
    #     ln = '{}{} {} {}'.format(
    #         self.measurement, tags, fields, time_stamp)
    #     return ln

    # def check_buffer(self):
    #     if len(self.data) > self.buffer_size:
    #         self._flush()

    # async def _check_and_send_to_database(self):
    #     """Checks the length of the data list and
    #     if long enough sends it to the database."""
    #
    #     try:
    #         while self.bus.running:
    #             if len(self.data) > self.data_length:
    #                 LOGGER.debug("buffer limit exceeded. Flushing data")
    #                 await self._flush()
    #             else:
    #                 await asyncio.sleep(5)
    #     except CancelledError:
    #         LOGGER.info("Test cancelled. Closing database.")
    #
    #     return

    def _prepare_data(self):
        if self.data:
            _data = '\n'.join(infl.create_measurement() for infl in self.data)
            _data += '\n'
            return _data
        return None

    def _flush(self):
        """Prepare data and write it to the database"""
        _data = self._prepare_data()

        if _data:
            self.data = []
            self.bus.add_async_task(self._send(_data))

    async def _send(self, data):
        resp = None
        try:
            LOGGER.debug("Flushing")
            with async_timeout.timeout(5, loop=self.bus.loop):
                LOGGER.debug("Writing data to database")
                resp = await self.bus.session.post(self.url,
                                                   data=data)
            if resp.status not in [204, 200]:
                raise FatalTestFailException(
                    "Wrong influx response code {}".format(resp.status))
        except (asyncio.TimeoutError, ClientError) as err:
            LOGGER.error(err)
            raise FatalTestFailException("Error sending data to database")
        finally:
            if resp is not None:
                await resp.release()

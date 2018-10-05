import asyncio
import logging

import async_timeout
from aiohttp.client_exceptions import ClientError
from slugify import slugify

from batterytester.components.datahandlers.base_data_handler import (
    BaseDataHandler
)
from batterytester.core.bus import Bus
from batterytester.core.helpers.constants import (
    ATTR_TIMESTAMP,
    KEY_VALUE,
    ATTR_VALUES,
    ATTR_SENSOR_NAME,
)
from batterytester.core.helpers.helpers import FatalTestFailException
from batterytester.core.helpers.message_data import AtomWarmup, ActorResponse

LOGGER = logging.getLogger(__name__)


# todo: handle actor response data.


def nesting(data: dict):
    def un_nest(key_prefix, dct: dict):
        for key in dct:
            if isinstance(dct[key], dict):
                un_nest(key_prefix + "_" + key, dct[key])
            else:
                data[key_prefix + "_" + key] = dct[key]

    for key in list(data):
        if isinstance(data[key], dict):
            un_nest(key, data[key])
            data.pop(key)

    return data


class InfluxLineProtocol:
    """https://docs.influxdata.com/influxdb/v1.5/
    write_protocols/line_protocol_tutorial/"""

    def __init__(
            self, measurement, time_stamp, tags: dict = None,
            fields: dict = None
    ):
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
        return " ".join(self.creator())

    def creator(self):
        if self._tags:
            yield "{},{}".format(
                self._measurement, line_protocol_fields(nesting(self._tags))
            )
        else:
            yield self._measurement
        if self._fields:
            yield line_protocol_fields(nesting(self._fields))
        yield str(to_nanoseconds(self._timestamp))


def line_protocol_fields(tags: dict):
    """Create the fields and their values.

    incoming is a dict with {KEY_VALUE:VALUE} structure.
    """

    def key_value_generator(pairs):
        for key, value in pairs:
            if isinstance(value, str):
                _val = '"{}"'.format(value)
                yield (key, _val)
            else:
                yield key, value

    return ",".join(
        (
            "{}={}".format(key, value)
            for key, value in key_value_generator(tags.items())
        )
    )


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
            "Unable to convert milliseconds to nanoseconds."
        )


def get_annotation_tags(data: dict):
    return ",".join(
        (
            "{} {}".format(slugify(key), slugify(str(value)))
            for key, value in data.items()
        )
    )


KEY_ATOM_NAME = "atom_name"


class Influx(BaseDataHandler):
    """Writes data to an InfluxDB database."""

    def __init__(
            self,
            *,
            host=None,
            database="menc",
            buffer_size=5,
            subscription_filters=None
    ):
        """
        :param host: ip address of the influx database
        :param database: The database to write data to.
        :param buffer_size: buffer length before call to influx api is made.
        :param subscription_filters: Filter subject subscriptions.

        For example:
            influx = Influx(subscription_filters=subj.ACTOR_RESPONSE_RECEIVED)
        """
        super().__init__(subscription_filters)
        self.host = host
        self.data = []
        self.bus = None
        self.url = "http://{}:8086/write?db={}".format(host, database)
        self.measurement = None  # actually the name of the test.
        self.buffer_size = buffer_size
        self._tags = {}

    async def setup(self, test_name, bus):
        self.bus = bus
        self.measurement = test_name

    async def shutdown(self, bus: Bus):
        _data = self._prepare_data()

        if _data:
            self.data = []
            await self._send(_data)

    def add_to_buffer(self, data: InfluxLineProtocol):
        """Add influx line data to buffer and check size"""
        self.data.append(data)
        if len(self.data) >= self.buffer_size:
            self._flush()

    def event_actor_response_received(self, testdata: ActorResponse):
        """Handle actor response data."""

        _annotation_tags = get_annotation_tags(testdata.response.value)

        try:
            _text = self._tags[KEY_ATOM_NAME]
        except KeyError:
            _text = "unknown"

        _influx = InfluxLineProtocol(
            self.measurement,
            testdata.time.value,
            fields={
                "title": testdata.subj,
                "text": _text,
                "tags": _annotation_tags,
            },
        )
        self.add_to_buffer(_influx)

    def event_atom_warmup(self, testdata: AtomWarmup):
        """Respond to warmup event.

        This data is stored as an event or so called annotation.
        For more info on storing and displaying annotations.
        """
        super().event_atom_warmup(testdata)

        self._tags["loop"] = testdata.loop.value
        self._tags["idx"] = testdata.idx.value
        self._tags[KEY_ATOM_NAME] = slugify(testdata.atom_name.value)

        annotation_tags = "loop {},index {}".format(
            testdata.loop.value, testdata.idx.value
        )
        _influx = InfluxLineProtocol(
            self.measurement,
            testdata.started.value,
            fields={
                "title": "atom_warmup",
                "text": self._tags[KEY_ATOM_NAME],
                "tags": annotation_tags,
            },
        )
        self.add_to_buffer(_influx)

    def event_test_warmup(self, testdata):
        """Handle test warmup data"""

        annotation_tags = "loops {}".format(testdata.loop_count.value)

        _influx = InfluxLineProtocol(
            self.measurement,
            testdata.started.value,
            fields={
                "title": "TEST START",
                "text": testdata.test_name.value,
                "tags": annotation_tags,
            },
        )
        self.add_to_buffer(_influx)
        self._flush()

    def event_sensor_data(self, testdata):
        influx = InfluxLineProtocol(
            self.measurement,
            testdata[ATTR_TIMESTAMP][ATTR_VALUES],
            tags=self._tags,
            fields={
                testdata[ATTR_SENSOR_NAME]: testdata[ATTR_VALUES][ATTR_VALUES]
            },
        )
        self.add_to_buffer(influx)

    def _prepare_data(self):
        if self.data:
            _data = "\n".join(infl.create_measurement() for infl in self.data)
            _data += "\n"
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
            with async_timeout.timeout(10, loop=self.bus.loop):
                LOGGER.debug("Flushing to database %s", data)
                resp = await self.bus.session.post(self.url, data=data)
            if resp.status not in [204, 200]:
                js = await resp.json()
                LOGGER.error(js)
                raise FatalTestFailException(
                    "Wrong influx response code {}".format(resp.status)
                )
        except (asyncio.TimeoutError, ClientError) as err:
            LOGGER.exception(err)
            raise FatalTestFailException("Error sending data to database")
        finally:
            if resp is not None:
                await resp.release()

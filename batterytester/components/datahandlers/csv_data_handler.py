import asyncio
import logging
import os
from asyncio import CancelledError
from concurrent.futures import ThreadPoolExecutor

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import \
    BaseDataHandler, create_report_file
from batterytester.core.helpers.constants import ATTR_SENSOR_NAME, KEY_VALUE, \
    ATTR_TIMESTAMP
from batterytester.core.helpers.helpers import get_localtime_string

LOGGER = logging.getLogger(__name__)

COL_SENSOR_NAME = 'sensor_name'
COL_TIME_STAMP = 'time_stamp'
COL_TIME_STRING = 'time_string'
COL_VALUE = 'value'


class CsvSensorData:
    def __init__(self, test_name, output_path, bus):
        self.test_name = test_name
        self.output_path = output_path
        self.file_name = None
        self.data = []
        self.separator = ';'
        self.value_keys = []
        self.bus = bus
        self.file_data_queue = asyncio.Queue(loop=self.bus.loop)
        self.bus.add_async_task(self.threaded_file_writer())

    async def threaded_file_writer(self, *args):
        with ThreadPoolExecutor(max_workers=1) as executor:
            res = await self.bus.loop.run_in_executor(
                executor, self.file_writer)
            return res

    def create_file_name(self, sensor_name):
        _fname = "{}_{}".format(self.test_name, sensor_name)
        self.file_name = create_report_file(
            _fname, None, self.output_path, extension='csv')

    def add_data(self, data):
        self.data.append(data)

    def create_columns(self, sensor_data):
        _cols = [COL_SENSOR_NAME, COL_TIME_STAMP, COL_TIME_STRING, COL_VALUE]

        self.file_data_queue.put_nowait(self.separator.join(_cols))

    def file_writer(self):
        while self.bus.running:
            _fut = asyncio.run_coroutine_threadsafe(
                self.file_data_queue.get(), self.bus.loop)
            _line = None
            try:
                _line = _fut.result(timeout=5)
            except asyncio.TimeoutError:
                _fut.cancel()
            except CancelledError:
                pass
            if _line:
                with open(self.file_name, 'a') as fl:
                    fl.write(_line)
                    fl.write('\n')
                    fl.flush()
                    os.fsync(fl.fileno())

        pass

    def get_values(self, sensor_data):
        vals = [sensor_data[ATTR_SENSOR_NAME],
                str(sensor_data[ATTR_TIMESTAMP][KEY_VALUE]),
                get_localtime_string(sensor_data[ATTR_TIMESTAMP][KEY_VALUE]),
                str(sensor_data[KEY_VALUE][KEY_VALUE])
                ]
        return self.separator.join(vals)

    def flush(self):
        if self.data:
            _data = '\n'.join(
                (self.get_values(_sensor_data) for _sensor_data in self.data))
            self.data = []
            self.file_data_queue.put_nowait(_data)


class CsvDataHandler(BaseDataHandler):
    """Create CSV file per connected sensor."""

    def __init__(self, write_buffer_size=1, output_path='csv'):
        super().__init__()
        self.sensor_data = {}
        self.write_buffer = write_buffer_size
        self.current_buffer = 0
        self.test_name = None
        self.output_path = output_path
        self.bus = None

    def get_subscriptions(self):
        return (
            (subj.SENSOR_DATA, self.sensor_data_received),
        )

    async def setup(self, test_name, bus):
        self.test_name = test_name
        self.bus = bus

    def sensor_data_received(self, subj, data):
        self.current_buffer += 1

        if data[ATTR_SENSOR_NAME] not in self.sensor_data:
            _sensor_data = CsvSensorData(
                self.test_name, self.output_path, self.bus)
            _sensor_data.create_file_name(data[ATTR_SENSOR_NAME])
            _sensor_data.create_columns(data)

            self.sensor_data[data[ATTR_SENSOR_NAME]] = _sensor_data

        self.sensor_data[data[ATTR_SENSOR_NAME]].add_data(data)

        if self.current_buffer >= self.write_buffer:
            self.current_buffer = 0
            self._flush()

    def _flush(self):
        for _sensor_data in self.sensor_data.values():
            _sensor_data.flush()

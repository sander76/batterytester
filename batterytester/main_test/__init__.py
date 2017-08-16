import asyncio
import json
import logging
import threading
from asyncio.futures import CancelledError

import aiohttp
import os

from batterytester.connector import SensorConnector
from batterytester.database import DataBase

from batterytester.helpers import Bus, get_current_time, check_output_location
from batterytester.report import Report

lgr = logging.getLogger(__name__)

BASE_TEST_LOCATION = 'test_results'



class BaseTest:
    def __init__(self,
                 testname: str,
                 sensor_data_connector: SensorConnector,
                 database: DataBase,
                 bus: Bus,
                 report: Report,
                 test_location=None):
        self.bus = bus
        self.test_name = testname
        self.sensor_data_connector = sensor_data_connector
        self.database = database
        self.bus.add_async_task(self._messager())
        self.bus.add_async_task(self.async_test())
        self.test_location = test_location
        self._report=report

    def handle_sensor_data(self, sensor_data):
        """Sensor data can influence the main test.
        (Like stopping the test depending on sensor data)
        """
        raise NotImplemented

    @asyncio.coroutine
    def _start_test(self):
        self._report.write_intro(self.test_name)
        self.started = get_current_time()

    @asyncio.coroutine
    def async_test(self):
        return

    @asyncio.coroutine
    def _messager(self):
        """Long running task.
        Gets data from the sensor_data_queue
        Data is passed to handle_sensor_data method for interpretation and
        interaction.

        Finally it is added to the database."""
        if self.sensor_data_connector:
            try:
                while self.bus.running:
                    sensor_data = yield from self.sensor_data_connector.sensor_data_queue.get()
                    self.handle_sensor_data(sensor_data)

                    yield from self.database.add_to_database(sensor_data)
                lgr.debug("stopping message loop.")
            except CancelledError as e:
                return

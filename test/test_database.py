import unittest
from unittest.mock import MagicMock

import asyncio

from batterytester.database import DataBase
from batterytester.helpers import get_bus
from batterytester.powerviewlongruntest import BaseTest


class TestBaseTest(unittest.TestCase):
    def setUp(self):
        self.database = DataBase("123.1.1.123", "testDatabase",
                                 "testMeasurement")
        self.connector_mock = MagicMock()
        self.connector_mock.sensor_data_queue = asyncio.Queue()

    def is_empty(self):
        bus = get_bus()
        tasks = asyncio.Task.all_tasks(bus.loop)
        self.assertEqual(len(tasks),0)

    def test_database_stop_test(self):
        self.is_empty()
        basetest1 = BaseTest(self.connector_mock, self.database)
        for i in range(31):
            basetest1.bus.add_async_task(
                basetest1.sensor_data_connector.sensor_data_queue.put({"test": 1}))
        self.assertEqual(basetest1.bus.start_test(),
                         "Problems writing data to database")

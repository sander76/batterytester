import unittest
from unittest.mock import MagicMock

import asyncio

from batterytester.arduino_connector import ThreadedSensorConnector
from batterytester.helpers import get_bus
from batterytester.powerviewlongruntest import BaseTest
from batterytester.database import DataBase

# from test.test_connector import EXIT_MESSAGE2

EXIT_MESSAGE1 = "stopping basetest at start"


class BaseTest1(BaseTest):
    def __init__(self, sensor_data_connector, database):
        BaseTest.__init__(self, sensor_data_connector, database)

    @asyncio.coroutine
    def test(self):
        self.bus.stop_test(EXIT_MESSAGE1)


# class ThreadedSensorConnector1(ThreadedSensorConnector):
#     def __init__(self, sensor_data_parser):
#         ThreadedSensorConnector.__init__(self, sensor_data_parser)
#
#     def connect(self):
#         self.bus.stop_test(EXIT_MESSAGE2)


class TestBaseTest(unittest.TestCase):
    def setUp(self):
        self.database = DataBase("123.1.1.123", "testDatabase",
                                 "testMeasurement")
        self.connector_mock = MagicMock()
        self.connector_mock.sensor_data_queue = asyncio.Queue()

    def is_empty(self):
        bus = get_bus()
        tasks = asyncio.Task.all_tasks(bus.loop)
        self.assertEqual(len(tasks), 0)

    def test_stop_test(self):
        self.is_empty()
        basetest = BaseTest1(self.connector_mock, self.database)
        self.assertEqual(basetest.bus.start_test(), EXIT_MESSAGE1)
        # self.is_empty()

        # def test_stop_test1(self):
        #     self.is_empty()
        #     threaded_sensor_connector = ThreadedSensorConnector1(MagicMock())
        #     basetest = BaseTest(threaded_sensor_connector, self.database)
        #     self.assertEqual(basetest.bus.start_test(), EXIT_MESSAGE2)

# class TestBaseTestCallback(unittest.TestCase):
#     def setUp(self):
#         database = DataBase("123.1.1.123", "testDatabase", "testMeasurement")
#         connector = ThreadedSensorConnector(MagicMock())
#         self.baseTest = BaseTest(connector, database)
#
#     def test_callback_stop_test1(self):
#         self.assertTrue(self.baseTest.bus.start_test())
#
#         # def test_add_database(self):
#         #     # add data to the loop.
#         #
#         #     _dbase = asyncio.gather(
#         #         *[self.baseTest.database.add_to_database({"test": 1}) for i in
#         #           range(31)])
#         #     try:
#         #         self.baseTest.loop.run_until_complete(_dbase)
#         #     except Exception as e:
#         #         pass
#         #     self.assertTrue(1, 1)
#         #
#         # def test_timeout(self):
#         #     pass

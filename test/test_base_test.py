# import unittest
# from unittest.mock import MagicMock
#
# import asyncio
#
# from batterytester.connector.arduino_connector import ThreadedSensorConnector
# from batterytester.database.influx import Influx

#
# from batterytester.database import DataBase
#
# # from test.test_connector import EXIT_MESSAGE2
# from batterytester.main_test import BaseTest
#
# EXIT_MESSAGE1 = "stopping basetest at start"
#
#
# class BaseTest1(BaseTest):
#     def __init__(self, sensor_data_connector, database):
#         BaseTest.__init__(self, sensor_data_connector, database)
#
#     @asyncio.coroutine
#     def test(self):
#         self.bus.stop_test(EXIT_MESSAGE1)
#
#
# class TestBaseTest(unittest.TestCase):
#     def setUp(self):
#         self.database = Influx("123.1.1.123", "testDatabase",
#                                  "testMeasurement")
#         self.connector_mock = MagicMock()
#         self.connector_mock.sensor_data_queue = asyncio.Queue()
#
#     def is_empty(self):

#         tasks = asyncio.Task.all_tasks(bus.loop)
#         self.assertEqual(len(tasks), 0)
#
#     def test_stop_test(self):
#         self.is_empty()
#         basetest = BaseTest1(self.connector_mock, self.database)
#         self.assertEqual(basetest.bus.start_test(), EXIT_MESSAGE1)

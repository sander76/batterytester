import unittest
from unittest.mock import MagicMock

import asyncio

from batterytester.arduino_connector import ThreadedSensorConnector
from batterytester.database import DataBase
from batterytester.helpers import get_bus
from batterytester.powerviewlongruntest import BaseTest

EXIT_MESSAGE2 = "stopping at serial connect"


class ThreadedSensorConnector1(ThreadedSensorConnector):
    def __init__(self, sensor_data_parser):
        ThreadedSensorConnector.__init__(self, sensor_data_parser)

    def connect(self):
        self.bus.stop_test(EXIT_MESSAGE2)


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

    def test_stop_test1(self):
        self.is_empty()
        threaded_sensor_connector = ThreadedSensorConnector1(MagicMock())
        basetest = BaseTest(threaded_sensor_connector, self.database)
        self.assertEqual(basetest.bus.start_test(), EXIT_MESSAGE2)

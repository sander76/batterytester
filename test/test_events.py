import unittest
from unittest import mock
from unittest.mock import MagicMock

import asyncio

from batterytester.database import DataBase

from batterytester.powerviewlongruntest import BaseTest
from batterytester.helpers import Bus

class Test1(BaseTest):
    def __init__(self, sensor_data_connector,
                 database):
        BaseTest.__init__(self,
                          sensor_data_connector,
                          database)

    @asyncio.coroutine
    def test(self):
        self.bus.stop_test("stopping the test")


class TestBaseTest(unittest.TestCase):
    def setUp(self):
        self.connector_mock = MagicMock()
        self.connector_mock.sensor_data_queue = asyncio.Queue()
        self.mock_database = DataBase("123", "database", "measurement")

    @mock.patch.object(Bus, 'stop_test')
    def test_stop_bus(self, mock_stop_test):
        base_test = Test1(self.connector_mock, self.mock_database)
        base_test.bus.start_test()
        mock_stop_test.assert_called_with("stopping the test")

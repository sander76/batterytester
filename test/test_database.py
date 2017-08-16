import unittest
from unittest import mock

from batterytester.database import DataBase
from batterytester.database.influx import Influx
from batterytester.helpers import Bus


class TestBaseTest(unittest.TestCase):
    def setUp(self):
        self.database = Influx("1.2.3.4", "database", "measurement")

    @mock.patch.object(Bus, 'stop_test')
    def test_database(self, mock_stop):
        self.database.bus.loop.run_until_complete(
            self.database._send({"test": 1}))
        mock_stop.assert_called_with("Problems writing data to database")

    def test_add_data_points(self):
        datapoints = {"volts": 10, "amps": 20}
        result = self.database._add_data_points(datapoints).split(',')
        self.assertCountEqual(result, ['amps=20', 'volts=10'])

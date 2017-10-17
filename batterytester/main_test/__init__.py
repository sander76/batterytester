import asyncio
import json
import logging
import os

from batterytester.helpers.sequence_test_helpers import SensorData
from batterytester.main_test.base_test import BaseTest
from batterytester.test_atom import find_reference_data

lgr = logging.getLogger(__name__)

BASE_TEST_LOCATION = 'test_results'


class BaseSequenceTest(BaseTest):
    def __init__(self, test_name,
                 loop_count, report, test_location,
                 reference_test_location, database=None,
                 sensor_data_connector=None,
                 learning_mode: bool = True,
                 telegram_token=None, chat_id=None):
        super().__init__(test_name, loop_count,
                         sensor_data_connector=sensor_data_connector,
                         database=database,
                         report=report,
                         test_location=test_location,
                         telegram_token=telegram_token,
                         telegram_chat_id=chat_id
                         )
        self._learning_mode = learning_mode
        self._reference_test_location = reference_test_location
        self.result_summary = [('loop', 'index', 'result')]

    async def perform_test(self, current_loop, idx, atom):
        """Performs an actual atom test."""
        # Executing a command performing an action on the
        # test subject.
        await atom.execute()

        # sleeping the defined duration to gather sensor
        # data which coming in as a result of the execution
        # command
        await asyncio.sleep(atom.duration)

        self.database.save(atom._sensor_data_file_name)

        current_sensor_data = SensorData(
            self._report, raw_sensor_data=atom.sensor_data)
        current_sensor_data.process_sensor_data()

        if not self._learning_mode:
            # Actual testing mode. reference data
            # and testing data can be compared.
            _ref_sensor_data = self.load_reference_sensor_data(idx)

            _success = atom.reference_compare()
            self.result_summary.append(
                (current_loop, idx, _success))

        self._report.write_summary_to_file()

    def load_reference_sensor_data(self, idx):
        _fname = find_reference_data(idx, self._reference_test_location)
        with open(
                os.path.join(self._reference_test_location, _fname),
                'r') as _fl:
            _raw_sensor_data = json.load(_fl)
        ref_sensor_data = SensorData(
            self._report, raw_sensor_data=_raw_sensor_data)
        ref_sensor_data.process_sensor_data(report=False)
        return ref_sensor_data

    async def atom_warmup(self, loop, atom):
        self.database.set_current_unit(
            atom.sensor_data)
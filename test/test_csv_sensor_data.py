from unittest.mock import Mock

import pytest

from batterytester.components.datahandlers.csv_data_handler import \
    CsvSensorData, COL_SENSOR_NAME, COL_TIME_STAMP, COL_TIME_STRING
from batterytester.components.sensor.incoming_parser import get_measurement


@pytest.fixture
def csv_sensor_data():
    bus = Mock()
    bus.add_async_task = Mock()
    sensor_data = CsvSensorData('test_test', 'out', bus)
    sensor_data._write_to_file = Mock()
    return sensor_data


@pytest.fixture
def fake_measurement():
    _measure = get_measurement('sensor_a', {'v': 10, 'a': 2})
    return _measure


def test_create_columns(csv_sensor_data: CsvSensorData, fake_measurement):
    csv_sensor_data.add_data(fake_measurement)
    assert len(csv_sensor_data.data) == 1

    csv_sensor_data.create_columns(fake_measurement)
    csv_sensor_data._write_to_file.assert_called_once_with(
        '{};{};{};v;a'.format(COL_SENSOR_NAME, COL_TIME_STAMP,COL_TIME_STRING))


def test_get_values(csv_sensor_data: CsvSensorData, fake_measurement):
    csv_sensor_data.add_data(fake_measurement)
    csv_sensor_data.create_columns(fake_measurement)
    _values = csv_sensor_data.get_values(fake_measurement)
    assert _values.startswith(_values)
    assert ';10;' in _values
    assert ';2' in _values


def test_flush(csv_sensor_data: CsvSensorData, fake_measurement):
    csv_sensor_data.add_data(fake_measurement)
    csv_sensor_data.create_columns(fake_measurement)
    csv_sensor_data.flush()
    assert csv_sensor_data.file_data_queue.qsize() == 2
    pass


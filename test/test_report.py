from pathlib import Path
from shutil import rmtree

import pytest

from batterytester.components.datahandlers.base_data_handler import \
    check_output_folder, create_report_file

TEST_FOLDER = 'testfolder'


@pytest.fixture()
def test_path():
    try:
        rmtree(Path(TEST_FOLDER))
        # Path.rmdir(Path(TEST_FOLDER))
    except FileNotFoundError:
        pass
    yield Path.cwd().joinpath(TEST_FOLDER)
    try:
        rmtree(Path(TEST_FOLDER))
    except FileNotFoundError:
        pass


def test_check_output_folder(test_path):
    path = check_output_folder(TEST_FOLDER)
    assert test_path == path


def test_check_output_folder_existing_folder(test_path):
    Path.mkdir(Path(TEST_FOLDER))
    path = check_output_folder(TEST_FOLDER)
    assert test_path == path


def test_check_output_folder_full_path(test_path):
    _full = str(Path.cwd().joinpath(TEST_FOLDER))
    path = check_output_folder(_full)
    assert test_path == path


def test_create_report_file(test_path):
    full = create_report_file('test_name', None, TEST_FOLDER)
    assert full.endswith('.md')
    assert 'test_name' in full
    full = create_report_file('test_name', 'report_name', TEST_FOLDER,
                              extension='xls')
    assert full.endswith('.xls')
    assert '.md' not in full
    assert 'report_name' in full

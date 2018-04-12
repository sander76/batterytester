from pathlib import Path

import pytest

from batterytester.components.datahandlers.report import check_output_folder

TEST_FOLDER = 'testfolder'


@pytest.fixture()
def test_path():
    try:
        Path.rmdir(Path(TEST_FOLDER))
    except FileNotFoundError:
        pass
    yield Path.cwd().joinpath(TEST_FOLDER)
    try:
        Path.rmdir(Path(TEST_FOLDER))
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

from pathlib import Path
from shutil import rmtree

import pytest

import batterytester.core.helpers.message_subjects as subj

from batterytester.components.datahandlers.base_data_handler import (
    check_output_folder,
    create_report_file,
)
from batterytester.components.datahandlers.report import Report

TEST_FOLDER = "testfolder"


@pytest.fixture()
def test_path():
    try:
        rmtree(str(Path(TEST_FOLDER)))
        # Path.rmdir(Path(TEST_FOLDER))
    except FileNotFoundError:
        pass
    yield Path.cwd().joinpath(TEST_FOLDER)
    try:
        rmtree(str(Path(TEST_FOLDER)))
    except FileNotFoundError:
        pass
    except PermissionError:
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
    full = create_report_file("test_name", None, TEST_FOLDER)
    assert full.endswith(".md")
    assert "test_name" in full
    full = create_report_file(
        "test_name", "report_name", TEST_FOLDER, extension="xls"
    )
    assert full.endswith(".xls")
    assert ".md" not in full
    assert "report_name" in full


def test_subscriptions():
    inf = Report()

    subs = inf.get_subscriptions()

    assert len(subs) == len(inf.subscriptions)
    for sub in subs:
        assert sub in inf.subscriptions

    inf = Report(subscription_filters=[subj.TEST_WARMUP])
    subs = [sub for sub in inf.get_subscriptions()]

    assert len(subs) == 1
    assert subs[0][0] == subj.TEST_WARMUP


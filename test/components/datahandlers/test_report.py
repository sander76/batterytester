from pathlib import Path
from shutil import rmtree
from unittest.mock import Mock

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


@pytest.fixture
def report():
    rep = Report()
    rep.event_test_finished = Mock()
    rep.event_test_fatal = Mock()
    rep.event_atom_result = Mock()
    rep.event_atom_warmup = Mock()
    rep.event_test_warmup = Mock()
    return rep


def test_events(report):
    test_data = {}

    report.handle_event(subj.TEST_FINISHED, test_data)
    report.event_test_finished.assert_called_once_with(test_data)

    report.handle_event(subj.TEST_FATAL, test_data)
    report.event_test_fatal.assert_called_once_with(test_data)

    report.handle_event(subj.ATOM_RESULT, test_data)
    report.event_atom_result.assert_called_once_with(test_data)

    report.handle_event(subj.ATOM_WARMUP, test_data)
    report.event_atom_warmup.assert_called_once_with(test_data)

    report.handle_event(subj.TEST_WARMUP, test_data)
    report.event_test_warmup.assert_called_once_with(test_data)



# def test_subscriptions():
#     inf = Report()
#
#     subs = inf.get_subscriptions()
#
#     assert len(subs) == len(inf.subscriptions)
#     for sub in subs:
#         assert sub in inf.subscriptions
#
#     inf = Report(subscription_filters=[subj.TEST_WARMUP])
#     subs = [sub for sub in inf.get_subscriptions()]
#
#     assert len(subs) == 1
#     assert subs[0][0] == subj.TEST_WARMUP

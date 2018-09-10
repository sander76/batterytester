from unittest.mock import Mock

import pytest

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.messaging import Messaging
from batterytester.core.helpers.message_data import TestWarmup


@pytest.fixture
def messaging():
    mess = Messaging()
    mess._send_to_ws = Mock()
    return mess


@pytest.fixture
def test_data():
    return Mock()
    # return TestData("noname", 1)


def do_test(messaging, subj, test_data):
    messaging.handle_event(subj, test_data)
    messaging._send_to_ws.assert_called_once_with(test_data)
    assert test_data.subj == subj


def test_event_test_warmup(messaging, test_data):
    do_test(messaging, subj.TEST_WARMUP, test_data)


def test_event_test_fatal(messaging, test_data):
    do_test(messaging, subj.TEST_FATAL, test_data)


def test_event_test_finished(messaging, test_data):
    do_test(messaging, subj.TEST_FINISHED, test_data)


def test_event_atom_result(messaging, test_data):
    messaging.handle_event(subj.ATOM_RESULT, test_data)
    assert messaging._send_to_ws.called


def test_event_sensor_data(messaging, test_data):
    messaging.handle_event(subj.SENSOR_DATA, test_data)
    assert messaging._send_to_ws.called

import logging
from unittest.mock import Mock

import batterytester.core.helpers.message_data as md
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers import message_subjects as subj
from batterytester.core.helpers.constants import ATOM_STATUS_EXECUTING, \
    ATOM_STATUS_COLLECTING
from batterytester.core.helpers.helpers import TestSetupException

from test.fake_components import FakeActor, FakeDataHandler, \
    FatalDataHandler, FatalSensorAsyncListenForData, FatalSensorProcess
from test.seqeuences import get_empty_sequence, get_sequence, \
    get_unknown_exception_sequence, get_fatal_exception_sequence, \
    get_non_fatal_exception_sequence, get_open_response_sequence, \
    get_reference_sequence

logging.basicConfig(level=logging.INFO)


def test_bound_loop():
    base_test = BaseTest(test_name='test', loop_count=2)
    loops = []
    for _loop in base_test._get_current_loop():
        loops.append(_loop)
    assert len(loops) == 2


def test_infinite_loop():
    base_test = BaseTest(test_name='test', loop_count=-1)
    loops = []
    counter = 0
    for _loop in base_test._get_current_loop():
        loops.append(_loop)
        counter += 1
        if counter == 10:
            break
    assert len(loops) == 10


def test_no_actor(base_test):
    """Using an actor which is not added to the test.
    Must raise a TestSetupException."""
    base_test.get_sequence = get_sequence
    base_test.start_test()
    # todo: a TestSetupException should also emit a notification ?
    assert isinstance(base_test.bus.exception, TestSetupException)


def test_notifications_empty_sequence(base_test):
    base_test.get_sequence = get_empty_sequence

    base_test.start_test()

    assert base_test.bus.notify.call_count == 4

    subjects = [subj.TEST_WARMUP,
                subj.LOOP_WARMUP,
                subj.LOOP_FINISHED,
                subj.TEST_FINISHED]

    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


def test_notifications_sequence(base_test):
    base_test.get_sequence = get_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_EXECUTE,
        subj.ATOM_COLLECTING,
        subj.LOOP_FINISHED,
        subj.TEST_FINISHED
    ]

    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj

    atom_status1 = base_test.bus.notify.call_args_list[3][0][1]
    atom_status2 = base_test.bus.notify.call_args_list[4][0][1]

    assert atom_status1.status == md.Data(ATOM_STATUS_EXECUTING)
    assert atom_status2.status == md.Data(ATOM_STATUS_COLLECTING)


def test_notifications_test_fail(base_test):
    """Test Notifications when an actor raises an unknown exception."""
    base_test.get_sequence = get_unknown_exception_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_EXECUTE,
        subj.TEST_FATAL
    ]

    assert len(base_test.bus.notify.call_args_list) == len(subjects)
    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


def test_notifications_fatal_test_fail(base_test):
    """Test notifications when an actor raises a fatal test exception."""
    base_test.get_sequence = get_fatal_exception_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_EXECUTE,
        subj.TEST_FATAL
    ]

    assert len(base_test.bus.notify.call_args_list) == len(subjects)
    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


def test_notifications_non_fatal_test_fail(base_test):
    """Test a not fatal actor exception"""
    base_test.get_sequence = get_non_fatal_exception_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_EXECUTE,
        subj.ATOM_RESULT,
        subj.LOOP_FINISHED,
        subj.TEST_FINISHED
    ]

    assert len(base_test.bus.notify.call_args_list) == len(subjects)
    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


def test_notification_actor_response(base_test: BaseTest):
    """Test where an actor returns a response"""

    base_test.get_sequence = get_open_response_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_EXECUTE,
        subj.ACTOR_RESPONSE_RECEIVED,
        subj.ATOM_COLLECTING,
        subj.LOOP_FINISHED,
        subj.TEST_FINISHED
    ]

    assert len(base_test.bus.notify.call_args_list) == len(subjects)
    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


def test_alternative_data_handler():
    test = BaseTest(test_name='test', loop_count=1)
    test.get_sequence = get_empty_sequence
    datahandler = FakeDataHandler()
    test.add_data_handlers(datahandler)
    test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.LOOP_FINISHED,
        subj.TEST_FINISHED]

    assert len(datahandler.calls) == len(subjects)
    for idx, subject in enumerate(subjects):
        assert subject == datahandler.calls[idx]


def test_fatal_data_handler():
    # todo: test fatal data handler

    test = BaseTest(test_name='test', loop_count=1)
    test.get_sequence = get_empty_sequence
    datahandler = FatalDataHandler(subj.TEST_WARMUP)
    test.add_data_handlers(datahandler)
    test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.TEST_FATAL]

    assert len(datahandler.calls) == len(subjects)
    for idx, subject in enumerate(subjects):
        assert subject == datahandler.calls[idx]


def test_fatal_atom_warmup_data_handler():
    # todo: Add more events where a datahandler failure can
    # happen.

    test = BaseTest(test_name='test', loop_count=1)
    test.get_sequence = get_sequence
    test.add_actor(FakeActor())

    datahandler = FatalDataHandler(subj.ATOM_WARMUP)
    test.add_data_handlers(datahandler)
    test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.TEST_FATAL
    ]

    assert len(datahandler.calls) == len(subjects)
    for idx, subject in enumerate(subjects):
        assert subject == datahandler.calls[idx]


def test_fatal_sensor():
    """Testing a sensor which is unable to read
    incoming sensor data."""
    test = BaseTest(test_name='test', loop_count=1)
    test.get_sequence = get_sequence
    test.add_actor(FakeActor())

    datahandler = FakeDataHandler()
    test.add_data_handlers(datahandler)

    test.add_sensors(FatalSensorAsyncListenForData())

    test.start_test()
    subjects = [
        subj.TEST_FATAL
    ]

    assert len(datahandler.calls) == len(subjects)
    for idx, subject in enumerate(subjects):
        assert subject == datahandler.calls[idx]


def test_fatal_sensor_on_process():
    """Testing a sensor which is unable to process incoming raw data"""
    test = BaseTest(test_name='test', loop_count=1)
    test.get_sequence = get_sequence
    test.add_actor(FakeActor())

    datahandler = FakeDataHandler()
    test.add_data_handlers(datahandler)

    test.add_sensors(FatalSensorProcess())

    test.start_test()
    subjects = [
        subj.TEST_FATAL
    ]

    assert len(datahandler.calls) == len(subjects)
    for idx, subject in enumerate(subjects):
        assert subject == datahandler.calls[idx]


def test_non_fatal_actor_boolean_reference_atom():
    test = BaseTest(test_name='test', loop_count=1)

    test.get_sequence = get_reference_sequence

    test.add_actor(FakeActor())

    _notify = Mock()
    test.bus.notify = _notify

    test.start_test()

    subjects = [
        (subj.TEST_WARMUP, md.TestWarmup),
        (subj.LOOP_WARMUP, md.LoopWarmup),
        (subj.ATOM_WARMUP, md.AtomWarmup),
        (subj.ATOM_EXECUTE, md.AtomExecute),
        (subj.ATOM_RESULT, md.AtomResult),
        (subj.LOOP_FINISHED, md.LoopFinished),
        (subj.TEST_FINISHED, md.TestFinished)
    ]

    assert len(subjects) == len(test.bus.notify.call_args_list)

    for idx, _call in enumerate(_notify.mock_calls):
        _subj = _call[1][0]
        _data = _call[1][1]
        assert _subj == subjects[idx][0]
        assert isinstance(_data, subjects[idx][1])


def test_setup_methods(base_test):
    """Test whether the setup and shutdown methods are called on an actor."""
    base_test.get_sequence = get_sequence
    actor = FakeActor()
    base_test.add_actor(actor)
    base_test.start_test()

    datahandler = FakeDataHandler

    actor._setup.assert_called_once_with(
        base_test.test_name, base_test.bus)

    actor._shutdown.assert_called_once_with(base_test.bus)

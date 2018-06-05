# todo: base test should test whether all notifications are called in the right
# order.
import logging

from batterytester.core.helpers import message_subjects as subj
from batterytester.core.helpers.constants import ATOM_STATUS_EXECUTING, \
    ATOM_STATUS_COLLECTING
from batterytester.core.helpers.helpers import TestSetupException
from batterytester.core.helpers.message_data import Data
from test.fake_components import FakeActor
from test.seqeuences import get_empty_sequence, get_sequence, \
    get_unknown_exception_sequence, get_fatal_exception_sequence, \
    get_non_fatal_exception_sequence

logging.basicConfig(level=logging.INFO)


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
        subj.ATOM_STATUS,
        subj.ATOM_STATUS,
        subj.LOOP_FINISHED,
        subj.TEST_FINISHED
    ]

    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj

    atom_status1 = base_test.bus.notify.call_args_list[3][0][1]
    atom_status2 = base_test.bus.notify.call_args_list[4][0][1]

    assert atom_status1.status == Data(ATOM_STATUS_EXECUTING)
    assert atom_status2.status == Data(ATOM_STATUS_COLLECTING)


def test_notifications_test_fail(base_test):
    # todo: this test actor raises an unknown exception. A known exception should
    # be tested too. like : NonFatalTestFailException and FatalTestFailException
    base_test.get_sequence = get_unknown_exception_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_STATUS,
        subj.TEST_FATAL
    ]

    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


def test_notifications_fatal_test_fail(base_test):
    base_test.get_sequence = get_fatal_exception_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_STATUS,
        subj.TEST_FATAL
    ]

    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


def test_notifications_non_fatal_test_fail(base_test):
    base_test.get_sequence = get_non_fatal_exception_sequence
    base_test.add_actor(FakeActor())
    base_test.start_test()

    subjects = [
        subj.TEST_WARMUP,
        subj.LOOP_WARMUP,
        subj.ATOM_WARMUP,
        subj.ATOM_STATUS,
        subj.ATOM_RESULT,
        subj.LOOP_FINISHED,
        subj.TEST_FINISHED
    ]

    for idx, _subj in enumerate(subjects):
        args, kwargs = base_test.bus.notify.call_args_list[idx]
        assert args[0] == _subj


# todo: test fatal data handler

# FakeDataHandler()


# todo: test fatal sensor


def test_setup_methods(base_test):
    """Test whether the setup and shutdown methods are called on an actor."""
    base_test.get_sequence = get_sequence
    actor = FakeActor()
    base_test.add_actor(actor)
    base_test.start_test()

    actor._setup.assert_called_once_with(
        base_test.test_name, base_test.bus)

    actor._shutdown.assert_called_once_with(base_test.bus)

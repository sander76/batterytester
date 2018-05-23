# todo: base test should test whether all notifications are called in the right
# order.
import logging
from unittest.mock import Mock

import pytest

import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers import message_subjects as subj
from batterytester.core.helpers.constants import ATOM_STATUS_EXECUTING, \
    ATOM_STATUS_COLLECTING
from batterytester.core.helpers.helpers import TestSetupException
from batterytester.core.helpers.message_data import Data
from test.fake_components import FakeActor

logging.basicConfig(level=logging.INFO)


def get_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.Atom(
            name='close shade',
            command=example_actor.close,
            duration=1
        ),
    )
    return _val


def get_empty_sequence(_actors):
    return []


def get_exception_sequence(_actors):
    example_actor = actor_tools._get_actor(_actors, 'fake_actor')

    _val = (
        atoms.Atom(
            name='exception action',
            command=example_actor.raise_exception,
            duration=1),
    )
    return _val


@pytest.fixture
def base_test():
    base_test = BaseTest(test_name='test', loop_count=1)
    base_test.bus.notify = Mock()
    return base_test


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
    base_test.get_sequence = get_exception_sequence
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

# todo: test fatal data handler

# todo: test fatal sensor

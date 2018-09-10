from unittest.mock import Mock

import pytest

from batterytester.components.datahandlers.base_data_handler import (
    BaseDataHandler
)
from batterytester.core.bus import Bus
from batterytester.core.helpers import message_subjects


class TestDataHandler(BaseDataHandler):
    async def setup(self, test_name: str, bus: Bus):
        pass


@pytest.fixture
def base_handler():
    handler = TestDataHandler()

    handler.event_test_fatal = Mock()
    handler.event_test_warmup = Mock()
    handler.event_test_result = Mock()
    handler.event_test_finished = Mock()

    handler.event_atom_result = Mock()
    handler.event_atom_collecting = Mock()
    handler.event_atom_execute = Mock()
    handler.event_atom_warmup = Mock()
    handler.event_atom_finished = Mock()

    handler.event_actor_response_received = Mock()
    return handler


def test_handle_event(base_handler):
    data = {}

    base_handler.handle_event(message_subjects.TEST_FATAL, data)
    base_handler.event_test_fatal.assert_called_with(data)

    base_handler.handle_event(message_subjects.TEST_WARMUP, data)
    base_handler.event_test_warmup.assert_called_with(data)

    base_handler.handle_event(message_subjects.TEST_FINISHED, data)
    base_handler.event_test_finished.assert_called_with(data)

    base_handler.handle_event(message_subjects.TEST_RESULT, data)
    base_handler.event_test_result.assert_called_with(data)

    base_handler.handle_event(message_subjects.ATOM_RESULT, data)
    base_handler.event_atom_result.assert_called_with(data)

    base_handler.handle_event(message_subjects.ATOM_EXECUTE, data)
    base_handler.event_atom_execute.assert_called_with(data)

    base_handler.handle_event(message_subjects.ATOM_COLLECTING, data)
    base_handler.event_atom_collecting.assert_called_with(data)

    base_handler.handle_event(message_subjects.ATOM_WARMUP, data)
    base_handler.event_atom_warmup.assert_called_with(data)

    base_handler.handle_event(message_subjects.ATOM_FINISHED, data)
    base_handler.event_atom_finished.assert_called_with(data)

    base_handler.handle_event(message_subjects.ACTOR_RESPONSE_RECEIVED, data)
    base_handler.event_actor_response_received.assert_called_with(data)


def test_handle_event_unsubscribed(base_handler):
    base_handler._subscriptions.actor_response_received = False
    data = {}

    base_handler.handle_event(message_subjects.ACTOR_RESPONSE_RECEIVED, data)
    base_handler.event_actor_response_received.assert_not_called()

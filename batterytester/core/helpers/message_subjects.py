"""Events emitted by the test.

Each event has a subject. A data handler can subscribe to these events."""

SUBJ = "subj"

"""
A `START` indicates an event and sends a start time as data.
A `WARMUP` sends the general info about the test, atom etc.
"""

PROCESS_INFO = "process_info"

PROCESS_STARTED = "process_started"

PROCESS_FINISHED = "process_finished"

PROCESS_MESSAGE = "process_message"

TEST_WARMUP = "test_warmup"
"""Emitted at the start of the test."""

TEST_FINISHED = "test_finished"
"""Emitted when a test has finished."""

TEST_RESULT = "test_result"
"""Emitted when a test result is available."""

TEST_FATAL = "test_fatal"
"""Emitted when a test has unexpectedly ended."""

ATOM_EXECUTE = "atom_execute"
"""Emitted when an actor has been executed."""

ATOM_COLLECTING = "atom_collecting"
"""Emitted when actor has """

ACTOR_RESPONSE_RECEIVED = "actor_response_received"
"""Emitted when an actor response has been received."""

ATOM_FINISHED = "atom_finished"
"""Emitted when an atom has finished."""

ATOM_WARMUP = "atom_warmup"
"""Emitted when an atom has warmed up."""

# ATOM_STATUS = 'atom_status'
# """Emitted when the status of an atom changes."""

ATOM_RESULT = "atom_result"
"""Emitted when an atom test result is available."""

RESULT_SUMMARY = "result_summary"
"""Emitted when a test summary is available."""

LOOP_WARMUP = "loop_warmup"
"""Emitted when a loop has warmed up."""

LOOP_FINISHED = "loop_finished"
"""Emitted when a loop has finished."""

SENSOR_DATA = "sensor_data"
"""Emitted when sensor data is received."""


class Subscriptions:
    def __init__(self):
        self.test_finished = True
        self.test_result = True
        self.test_warmup = True
        self.actor_executed = True
        self.actor_response_received = True
        self.atom_finished = True
        self.atom_warmup = True
        self.atom_execute = True
        self.atom_collecting = True
        self.atom_result = True
        self.result_summary = True
        self.loop_warmup = True
        self.loop_finished = True
        self.sensor_data = True
        self.test_fatal = True

    @classmethod
    def all_false(cls):
        sub = cls()
        sub.test_finished = False
        sub.test_result = False
        sub.test_warmup = False
        sub.actor_executed = False
        sub.actor_response_received = False
        sub.atom_finished = False
        sub.atom_warmup = False
        sub.atom_execute = False
        sub.atom_collecting = False
        sub.atom_result = False
        sub.result_summary = False
        sub.loop_warmup = False
        sub.loop_finished = False
        sub.sensor_data = False
        sub.test_fatal = False
        return sub

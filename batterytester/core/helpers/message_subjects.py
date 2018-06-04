"""Events emitted by the test.

Each event has a subject. A data handler can subscribe to these events."""

SUBJ = 'subj'

"""
A `START` indicates an event and sends a start time as data.
A `WARMUP` sends the general info about the test, atom etc.
"""

PROCESS_INFO = 'process_info'

PROCESS_STARTED = 'process_started'

TEST_FINISHED = 'test_finished'
"""Emitted when a test has finished."""

TEST_RESULT = 'test_result'
"""Emitted when a test result is available."""

TEST_WARMUP = 'test_warmup'
"""Emitted at the start of the test."""

ACTOR_EXECUTED = 'actor_executed'
"""Emitted when an actor has been executed."""

ACTOR_RESPONSE_RECEIVED = 'actor_response_received'
"""Emitted when an actor response has been received."""

ATOM_FINISHED = 'atom_finished'
"""Emitted when an atom has finished."""

ATOM_WARMUP = 'atom_warmup'
"""Emitted when an atom has warmed up."""

ATOM_STATUS = 'atom_status'
"""Emitted when the status of an atom changes."""

ATOM_RESULT = 'atom_result'
"""Emitted when an atom test result is available."""

RESULT_SUMMARY = 'result_summary'
"""Emitted when a test summary is available."""

LOOP_WARMUP = 'loop_warmup'
"""Emitted when a loop has warmed up."""

LOOP_FINISHED = 'loop_finished'
"""Emitted when a loop has finished."""

SENSOR_DATA = 'sensor_data'
"""Emitted when sensor data is received."""

TEST_FATAL = 'test_fatal'
"""Emitted when a test has unexpectedly ended."""

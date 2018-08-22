"""A simple test."""

import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.components.datahandlers as datahandlers
import batterytester.components.sensor as sensors
import batterytester.core.atom as atoms
from batterytester.components.sensor.volts_amps_sensor import VoltsAmpsSensor
from batterytester.core.base_test import BaseTest

# Define a test. Give it a proper name and define the amount
# of loops to run.
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

test = BaseTest(test_name='empty test', loop_count=100)

# Add actors to the test.
test.add_actor(
    actors.ExampleActor()
)

# Add sensors to the test.
test.add_sensors(
    VoltsAmpsSensor(serial_port='COM4')
)

# Add data handlers to the test.
test.add_data_handlers(
    datahandlers.Messaging()
)


# Each test (each loop) runs a sequence of tests to perform.
# The following method defines this sequence.
# Explained later in this document.
def get_sequence(_actors):
    example_actor = actor_tools.get_example_actor(_actors)

    _val = [
        atoms.Atom(
            name='open shade',
            duration=10,
            command=example_actor.open
        )
    ]
    return _val



test.get_sequence = get_sequence

test.start_test()

"""A led-gate test."""

# All imports. Please leave alone.
import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
from batterytester.components.actors.example_actor import ExampleActor
from batterytester.components.datahandlers.messaging import Messaging
from batterytester.components.sensor.volts_amps_sensor import VoltsAmpsSensor
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

# Define a test. Give it a proper name and define the amount
# of loops to run.
test = BaseTest(test_name="volts amps test", loop_count=20)

# Add actors to the test.
test.add_actor(ExampleActor())

# Add sensors to the test.
test.add_sensors(VoltsAmpsSensor(serial_port="COM4"))

# Add data handlers to the test.
test.add_data_handlers(Messaging())


# Each test (each loop) runs a sequence of tests to perform.
# The following method defines this sequence.
# Explained later in this document.
def get_sequence(_actors):
    example_actor = actor_tools.get_example_actor(_actors)

    _val = (
        atoms.Atom(name="close shade", command=example_actor.close, duration=5),
        atoms.Atom(name="open shade", duration=5, command=example_actor.open),
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

"""A simple Arduino test."""

# All imports. Please leave alone.
import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
import batterytester.components.datahandlers as datahandlers
import batterytester.components.sensor as sensors
from batterytester.components.datahandlers.console_data_handler import \
    ConsoleDataHandler
from batterytester.components.sensor.arduino_sensor_test import ArduinoSensor
from batterytester.core.base_test import BaseTest

# Define a test. Give it a proper name and define the amount
# of loops to run.
test = BaseTest(test_name='Arduino test', loop_count=3)

# Add actors to the test.
test.add_actor(
    actors.ExampleActor()
)

# Add sensors to the test.
test.add_sensors(
    ArduinoSensor(serial_port="COM6")
)

# Add data handlers to the test.
test.add_data_handlers(
    #todo: a "test fatal" event is emitted. but test is not fatal.
    ConsoleDataHandler()
)


# Each test (each loop) runs a sequence of tests to perform.
# The following method defines this sequence.
# Explained later in this document.
def get_sequence(_actors):
    example_actor = actor_tools.get_example_actor(_actors)

    _val = (
        atoms.Atom(
            name='close shade',
            command=example_actor.close,
            duration=2
        ),
        atoms.Atom(
            name='open shade',
            duration=2,
            command=example_actor.open
        )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

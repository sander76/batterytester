"""A csv report test."""

# All imports. Please leave alone.
import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
import batterytester.components.datahandlers as datahandlers
import batterytester.components.sensor as sensors
from batterytester.core.base_test import BaseTest

# Define a test. Give it a proper name and define the amount
# of loops to run.
test = BaseTest(test_name='csv test', loop_count=3)

# Add actors to the test.
test.add_actor(
    actors.ExampleActor()
)

# Add sensors to the test.
test.add_sensors(
    #sensors.FakeVoltsAmpsSensor(delay=2),
    #sensors.FakeVoltsAmpsSensor(sensor_prefix='abc')
    sensors.LedGateSensor(serial_port='COM6')
)

# Add data handlers to the test.
test.add_data_handlers(
    datahandlers.CsvDataHandler()
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
            duration=5
        ),
        atoms.Atom(
            name='open shade',
            duration=5,
            command=example_actor.open
        )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

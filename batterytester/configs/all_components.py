"""A simple test."""

# All imports. Please leave alone.
import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.components.datahandlers as datahandlers
import batterytester.components.sensor as sensors
import batterytester.core.atom as atoms
from batterytester.core.base_test import BaseTest

# Define a test. Give it a proper name and define the amount
# of loops to run.
test = BaseTest(test_name='empty test', loop_count=3)

# Add actors to the test.
test.add_actor(
    actors.ExampleActor(),
    actors.RelayActor(serial_port='/dev/port_2'),
    actors.PowerViewActor(hub_ip='172.22.3.4')
)

# Add sensors to the test.
test.add_sensors(
    sensors.FakeVoltsAmpsSensor(),
    sensors.LedGateSensor(serial_port='/dev/port_1')
)

# Add data handlers to the test.
test.add_data_handlers(
    datahandlers.Report(),
    datahandlers.Influx(host='172.22.3.6'),
    datahandlers.Messaging(host='172.0.0.1')
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

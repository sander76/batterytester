"""Test with multiple led gate squids."""
from batterytester.components.actors.example_actor import ExampleActor
from batterytester.components.actors.tools import get_example_actor
from batterytester.components.datahandlers.messaging import Messaging
from batterytester.components.sensor.fake_led_gate_sensor import \
    FakeLedGateSensor
from batterytester.core.atom import Atom, BooleanReferenceAtom
from batterytester.core.base_test import BaseTest

# Define a test. Give it a proper name and define the amount
# of loops to run.
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

test = BaseTest(test_name="multi ledgate test", loop_count=2)

# Add actors to the test.
test.add_actor(ExampleActor())

# Add sensors to the test.
test.add_sensors(FakeLedGateSensor(sensor_prefix="squid_1"),
                 FakeLedGateSensor())

# Add data handlers to the test.
test.add_data_handlers(Messaging())


# Each test (each loop) runs a sequence of tests to perform.
# The following method defines this sequence.
# Explained later in this document.
def get_sequence(_actors):
    example_actor = get_example_actor(_actors)

    _val = (
        BooleanReferenceAtom(
            name="close shade",
            command=example_actor.close,
            duration=5,
            reference={"6": True},
        ),
        Atom(name="open shade", duration=5, command=example_actor.open),
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

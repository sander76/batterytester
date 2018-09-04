"""A simple test."""

# All imports. Please leave alone.
import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
from batterytester.components.actors.example_actor import ExampleActor
from batterytester.components.actors.power_view_actor import PowerViewActor
from batterytester.components.actors.relay_actor import RelayActor
from batterytester.components.datahandlers.influx import Influx
from batterytester.components.datahandlers.messaging import Messaging
from batterytester.components.datahandlers.report import Report
from batterytester.components.sensor.fake_volts_amps_sensor import \
    FakeVoltsAmpsSensor
from batterytester.components.sensor.led_gate_sensor import LedGateSensor
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

# Define a test. Give it a proper name and define the amount
# of loops to run.
test = BaseTest(test_name='empty test', loop_count=3)

# Add actors to the test.
test.add_actor(
    ExampleActor(),
    RelayActor(serial_port='/dev/port_2'),
    PowerViewActor(hub_ip='172.22.3.4')
)

# Add sensors to the test.
test.add_sensors(
    FakeVoltsAmpsSensor(),
    LedGateSensor(serial_port='/dev/port_1')
)

# Add data handlers to the test.
test.add_data_handlers(
    Report(),
    Influx(host='172.22.3.6'),
    Messaging(host='172.0.0.1')
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

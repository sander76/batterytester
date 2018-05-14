# All imports. Please leave alone.
import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.components.datahandlers as datahandlers
import batterytester.core.atom as atoms
from batterytester.components.sensor.fake_led_gate_sensor import \
    FakeLedGateSensor
from batterytester.core.base_test import BaseTest

test = BaseTest(test_name='influx test', loop_count=1)

test.add_sensors(
    FakeLedGateSensor(delay=2)
)

test.add_actor(
    actors.ExampleActor()
)

test.add_data_handlers(
    datahandlers.Influx(host='172.22.3.21', database='menc')
    #datahandlers.ConsoleDataHandler()
    # Messaging()
)


def get_sequence(actors):
    example = actor_tools.get_example_actor(actors)

    _val = (
        atoms.Atom(
            name='open',
            command=example.open,
            duration=4
        ),
        atoms.Atom(
            name='activate 2',
            command=example.close,
            duration=4
        )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

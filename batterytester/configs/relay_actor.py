
# All imports. Please leave alone.
import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
import batterytester.components.datahandlers as datahandlers
import batterytester.components.sensor as sensors
from batterytester.core.base_test import BaseTest

test = BaseTest(test_name='relay test', loop_count=20)

test.add_sensors(
)

test.add_actor(
    actors.RelayActor(serial_port='COM4')
)

test.add_data_handlers(
    # Messaging()
)


def get_sequence(actors):
    relay = actor_tools.get_relay_actor(actors)

    actor1 = 4  # arduino pin 2
    actor2 = 5  # arduino pin 2

    _val = (
        atoms.Atom(
            name='activate 1',
            command=relay.activate,
            arguments={"pin": actor1},
            duration=3
        ),
        atoms.Atom(
            name='activate 2',
            command=relay.activate,
            arguments={"pin": actor2},
            duration=3
        )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()
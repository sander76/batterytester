# All imports. Please leave alone.
import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
from batterytester.components.actors.relay_actor import RelayActor
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

test = BaseTest(test_name="relay test", loop_count=20)

test.add_sensors()

test.add_actor(RelayActor(serial_port="COM6"))

test.add_data_handlers(
    # Messaging()
)


def get_sequence(actors):
    relay = actor_tools.get_relay_actor(actors)

    actor1 = 4  # arduino pin 4
    # actor2 = 5  # arduino pin 2

    _val = (
        atoms.Atom(
            name="activate 1",
            command=relay.activate,
            arguments={"pin": actor1},
            duration=3,
        ),
        # atoms.Atom(
        #     name='activate 2',
        #     command=relay.activate,
        #     arguments={"pin": actor2},
        #     duration=3
        # )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

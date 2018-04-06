from batterytester.core.actors.base_actor import ACTOR_TYPE_RELAY_ACTOR
from batterytester.core.actors.relay_actor import RelayActor
from batterytester.core.atom import Atom
from batterytester.main_test.base_test import BaseTest

test = BaseTest(test_name='relay test', loop_count=20)

test.add_sensors(
)

test.add_actor(
    RelayActor('COM4')
)

test.add_data_handlers(
    # Messaging()
)


def get_sequence(actors):
    relay = actors[ACTOR_TYPE_RELAY_ACTOR]  # type: RelayActor

    actor1 = 2  # arduino pin 2
    actor2 = 3  # arduino pin 2

    _val = (
        Atom(
            name='activate 1',
            command=relay.activate,
            arguments={"pin": actor1},
            duration=3
        ),
        Atom(
            name='activate 2',
            command=relay.activate,
            arguments={"pin": actor2},
            duration=3
        )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

from batterytester.core.actors.base_actor import ACTOR_TYPE_EXAMPLE
from batterytester.core.actors.example_actor import ExampleActor
from batterytester.core.atom.atom import Atom
from batterytester.core.datahandlers.messaging import Messaging
from batterytester.core.sensor.fake_volts_ir_sensor import FakeVoltsAmpsSensor
from batterytester.main_test.base_test import BaseTest


test = BaseTest(test_name='empty test', loop_count=20)

test.add_sensors(
    FakeVoltsAmpsSensor()
)

test.add_actor(
    ExampleActor()
)

test.add_data_handlers(
    Messaging()
)


def get_sequence(actors):
    example_actor = actors[ACTOR_TYPE_EXAMPLE]
    _val = (
        Atom(
            name='close shade',
            command=example_actor.close,
            duration=10
        ),
        Atom(name='open shade',
             duration=10,
             command=example_actor.open
             )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

# All imports. Please leave alone.
import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.components.datahandlers as datahandlers
import batterytester.core.atom as atoms
from batterytester.components.sensor import FakeVoltsAmpsSensor
from batterytester.components.sensor.fake_led_gate_sensor import \
    FakeLedGateSensor
from batterytester.components.sensor.volts_amps_sensor import VoltsAmpsSensor
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

test = BaseTest(test_name='new influx test', loop_count=20)

test.add_sensors(

)

test.add_actor(
    actors.ExampleActor()
)

test.add_data_handlers(

    datahandlers.Influx(host='172.22.3.21', database='menc'),
    #datahandlers.ConsoleDataHandler()
)


def get_sequence(actors):
    example = actor_tools.get_example_actor(actors)

    _val = (
        atoms.Atom(
            name='open',
            command=example.open,
            duration=1
        ),
        atoms.Atom(
            name='activate 2',
            command=example.close,
            duration=1
        )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

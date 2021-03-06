# All imports. Please leave alone.
import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
from batterytester.components.actors.example_actor import ExampleActor
from batterytester.components.datahandlers.influx import Influx
from batterytester.components.sensor.volts_amps_sensor import VoltsAmpsSensor
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

test = BaseTest(test_name="new influx test", loop_count=5)

test.add_sensors(VoltsAmpsSensor(serial_port="COM4"))

test.add_actor(ExampleActor())

test.add_data_handlers(Influx(host="172.22.3.21", database="menc"))


def get_sequence(actors):
    example = actor_tools.get_example_actor(actors)

    _val = (
        atoms.Atom(name="open", command=example.open, duration=2),
        atoms.Atom(name="activate 2", command=example.close, duration=2),
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

"""Bofu motor test."""

import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
from batterytester.components.actors.example_actor import ExampleActor
from batterytester.components.datahandlers.influx import Influx
from batterytester.components.datahandlers.messaging import Messaging
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

test = BaseTest(test_name="Somfy battery motor test", loop_count=10)

test.add_sensors()

test.add_actor(ExampleActor())

test.add_data_handlers(Messaging(), Influx(host="172.22.3.21", database="menc"))


def get_sequence(_actors):
    """Sequence of tests to perform."""
    relay = actor_tools.get_relay_actor(_actors)

    open_pin = 5
    close_pin = 4

    _val = (
        atoms.BooleanReferenceAtom(
            name="close shade",
            command=relay.activate,
            arguments={"pin": close_pin},
            duration=480,
            reference={"7": False, "5": False},
        ),
        atoms.BooleanReferenceAtom(
            name="open shade",
            command=relay.activate,
            arguments={"pin": open_pin},
            duration=480,
            reference={"7": True, "5": True},
        ),
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

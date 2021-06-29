"""A PowerView hub firmware checker test."""

# All imports. Please leave alone.

import batterytester.components.actors.tools as actor_tools
import batterytester.core.atom as atoms
import batterytester.core.helpers.message_subjects as subj
from batterytester.components.actors.powerview_version_checker import (
    PowerViewVersionChecker,
)
from batterytester.components.datahandlers.influx import Influx
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

# Define a test. Give it a proper name and define the amount
# of loops to run.
test = BaseTest(test_name="PowerView version checker", loop_count=-1)

# Add actors to the test.
test.add_actor(PowerViewVersionChecker(hub_ip="192.168.1.11"))

# Add sensors to the test.
test.add_sensors()

sub_filter = subj.Subscriptions.all_false()
sub_filter.actor_response_received = True

# Add data handlers to the test.
test.add_data_handlers(
    # Messaging(),
    # ConsoleDataHandler(),
    Influx(
        host="172.22.3.21",
        database="menc",
        buffer_size=1,
        subscription_filters=sub_filter,
    )
)


# Each test (each loop) runs a sequence of tests to perform.
# The following method defines this sequence.
# Explained later in this document.
def get_sequence(_actors):
    version_actor = actor_tools.get_powerview_version_checker_actor(_actors)

    _val = (
        atoms.Atom(
            name="check_version", command=version_actor.get_version, duration=1800
        ),
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

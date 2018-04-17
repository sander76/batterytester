"""A simple test."""

import batterytester.components.actors as actors
import batterytester.components.actors.tools as actor_tools
import batterytester.components.datahandlers as datahandlers
import batterytester.core.atom as atoms
# All imports. Please leave alone.
from batterytester.configs.secret import telegram_token, telegram_sander
from batterytester.core.base_test import BaseTest

# Define a test. Give it a proper name and define the amount
# of loops to run.
test = BaseTest(test_name='telegram test', loop_count=1)

# Add actors to the test.
test.add_actor(
    actors.ExampleActor()
)

# Add sensors to the test.
test.add_sensors(
    # sensors.FakeVoltsAmpsSensor()
)

# Add data handlers to the test.
test.add_data_handlers(
    # datahandlers.Report()
    datahandlers.Telegram(token=telegram_token, chat_id=telegram_sander)
    # test_frame.datahandler_slack()
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
            duration=4
        ),
        atoms.Atom(
            name='open shade',
            duration=4,
            command=example_actor.open
        )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

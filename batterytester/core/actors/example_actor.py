from batterytester.core.actors.base_actor import BaseActor, ACTOR_TYPE_EXAMPLE
from batterytester.core.bus import Bus


class ExampleActor(BaseActor):
    actor_type = ACTOR_TYPE_EXAMPLE

    def __init__(self):
        self.test_name = None

    async def open(self):
        print("open {}".format(self.test_name))

    async def close(self):
        print("close {}".format(self.test_name))

    async def setup(self, test_name: str, bus: Bus):
        """Initialize method.

        Executed before starting the actual test.
        Cannot be an infinite task. Needs to return for the main test to
        start."""
        self.test_name = test_name

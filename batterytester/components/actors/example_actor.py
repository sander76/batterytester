"""Example actor"""
from batterytester.components.actors.base_actor import (
    BaseActor,
    ACTOR_TYPE_EXAMPLE,
)
from batterytester.core.bus import Bus


class ExampleActor(BaseActor):
    """Example actor which exposes prints out data to the console."""

    actor_type = ACTOR_TYPE_EXAMPLE

    def __init__(self):
        self.test_name = None

    async def open(self):
        """Print open command.

        *Actor command*
        """
        pass
        # print("open {}".format(self.test_name))

    async def close(self):
        """Print close command.

        *Actor command*
        """
        pass
        # print("close {}".format(self.test_name))

    async def setup(self, test_name: str, bus: Bus):
        self.test_name = test_name

from abc import ABCMeta, abstractmethod

from batterytester.core.bus import Bus

ACTOR_TYPE_BASE = 'base_actor'
ACTOR_TYPE_EXAMPLE = 'example_actor'
ACTOR_TYPE_POWER_VIEW = 'powerview_actor'
"""PowerView actor."""
ACTOR_TYPE_RELAY_ACTOR = 'relay_actor'
"""Relay actor."""
ACTOR_TYPE_POWERVIEW_VERSION_CHECKER = 'pv_version_checker'


class BaseActor(metaclass=ABCMeta):
    actor_type = ACTOR_TYPE_BASE

    @abstractmethod
    async def setup(self, test_name: str, bus: Bus):
        """Initialize the actor.

        This is run before starting the actual test.
        Must return for the test to start.

        :param test_name: Name of the test
        :param bus: The bus
        :return:
        """
        pass

    async def shutdown(self, bus: Bus):
        """Shutdown the actor

        Is run at the end of the test.

        :param bus: the bus.
        :return:
        """
        pass

    async def warmup(self):
        """Warmup

        Commands emitted to the device connected to the actor to get the
        device into the appropriate state to start the test.

        :return:
        """
        pass

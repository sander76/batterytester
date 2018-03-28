from abc import ABCMeta, abstractmethod

from batterytester.core.bus import Bus

ACTOR_TYPE_BASE = 'base_actor'
ACTOR_TYPE_POWER_VIEW = 'powerview_actor'
ACTOR_TYPE_EXAMPLE = 'example_actor'


class BaseActor(metaclass=ABCMeta):
    actor_type = ACTOR_TYPE_BASE

    @abstractmethod
    async def setup(self, test_name: str, bus: Bus):
        """Initialize method.

        Executed before starting the actual test.
        Cannot be an infinite task. Needs to return for the main test to
        start."""
        pass

    async def warmup(self):
        pass

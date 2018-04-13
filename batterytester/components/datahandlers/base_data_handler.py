from abc import ABCMeta, abstractmethod

from batterytester.core.bus import Bus
from batterytester.core.helpers.message_data import AtomData


class BaseDataHandler(metaclass=ABCMeta):
    def __init__(self):
        self._current_idx = None
        self._current_loop = None
        self.test_name = None
        self._atom_name = None
        self._bus = None
        self.ready = False

    @abstractmethod
    async def setup(self, test_name: str, bus: Bus):
        """Initialize method.

        Executed before starting the actual test.
        Cannot be an infinite task. Needs to return for the main test to
        start."""
        pass

    async def shutdown(self, bus: Bus):
        """Shutdown the data handler

        Is run at the end of the test.

        :param bus: the bus.
        :return:
        """
        pass

    def _atom_warmup(self, subject, data: AtomData):
        self._current_idx = data.idx.value
        self._current_loop = data.loop.value
        self._atom_name = data.atom_name.value

    @abstractmethod
    def get_subscriptions(self):
        pass

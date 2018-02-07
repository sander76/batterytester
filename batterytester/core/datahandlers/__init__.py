from batterytester.core.helpers.message_data import AtomData


class BaseDataHandler:
    def __init__(self):
        self._current_idx = None
        self._current_loop = None
        self._atom_name = None

    def _atom_warmup(self, subject, data: AtomData):
        self._current_idx = data.idx.value
        self._current_loop = data.loop.value
        self._atom_name = data.atom_name.value

    def get_subscriptions(self):
        pass

    async def stop_data_handler(self):
        pass

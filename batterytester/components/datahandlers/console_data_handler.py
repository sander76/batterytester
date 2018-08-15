from pprint import pprint

import batterytester.core.helpers.message_subjects as subj
from batterytester.components.datahandlers.base_data_handler import (
    BaseDataHandler
)
from batterytester.core.helpers.message_data import (
    FatalData,
    TestFinished,
    TestData,
    AtomData,
    AtomStatus,
    AtomResult,
    LoopData,
    ActorResponse,
)


class ConsoleDataHandler(BaseDataHandler):
    """Console messaging."""

    def __init__(self, subscription_filters=None):
        super().__init__(subscription_filters)
        self.subscriptions = (
            (subj.TEST_WARMUP, self.test_warmup),
            (subj.TEST_FATAL, self.test_fatal),
            (subj.TEST_FINISHED, self.test_finished),
            (subj.ATOM_STATUS, self.atom_status),
            (subj.LOOP_WARMUP, self.loop_warmup),
            (subj.ATOM_WARMUP, self._atom_warmup),
            (subj.ATOM_RESULT, self.atom_result),
            (subj.SENSOR_DATA, self.test_data),
            (subj.ACTOR_RESPONSE_RECEIVED, self.response_received),
        )

    def to_console(self, data):
        pprint(data)

    def response_received(self, subject, data: ActorResponse):
        self.to_console("ACTOR RESPONSE DATA")
        self.to_console(data.to_dict())

    def loop_warmup(self, subject, data: LoopData):
        self.to_console("LOOP WARMUP")
        self.to_console(data.to_dict())

    def _atom_warmup(self, subject, data: AtomData):
        super()._atom_warmup(subject, data)
        self.to_console("ATOM WARMUP")
        self.to_console(data.to_dict())

    def test_warmup(self, subject, data: TestData):
        # LOGGER.debug("warmup test: {} data: {}".format(subject, data))
        self.to_console("TEST WARMUP")
        self.to_console(data.to_dict())

    def test_fatal(self, subject, data: FatalData):
        self.to_console("TEST FATAL")
        self.to_console(data.to_dict())

    def test_finished(self, subject, data: TestFinished):
        self.to_console("TEST FINISHED")
        self.to_console(data.to_dict())

    def atom_result(self, subject, data: AtomResult):
        """Sends out a summary of the current running test result."""
        self.to_console("ATOM RESULT")
        self.to_console(data.to_dict())

    def test_data(self, subject, data):
        self.to_console("SENSOR DATA")
        self.to_console(data)

    def atom_status(self, subject, data: AtomStatus):
        self.to_console("ATOM STATUS")
        self.to_console(data.to_dict())

    async def setup(self, test_name, bus):
        self._bus = bus
        self.test_name = test_name

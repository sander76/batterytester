import logging
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional

from batterytester.core.bus import Bus
from batterytester.core.helpers import message_subjects
from batterytester.core.helpers.helpers import get_current_time_string
from batterytester.core.helpers.message_data import AtomWarmup
from batterytester.core.helpers.message_subjects import Subscriptions

LOGGER = logging.getLogger(__name__)


def create_report_file(test_name, report_name, output_path, extension="md"):
    """Create a report file."""
    _base_filename = report_name or test_name
    _filename = "{}_{}.{}".format(
        _base_filename, get_current_time_string(), extension
    )

    _path = check_output_folder(output_path)
    # converting the Path object to string for Python 3.5 compatibility.
    _full = str(_path.joinpath(_filename))
    open(_full, "a").close()
    return _full


def check_output_folder(output_path) -> Path:
    _path = Path(output_path)
    if not _path.is_absolute():
        _path = Path.cwd().joinpath(_path)
    try:
        _path.mkdir(parents=True)
    except FileExistsError:
        LOGGER.debug("Path already exists.")
    return _path


class BaseDataHandler(metaclass=ABCMeta):
    subscriptions = ()

    def __init__(self, subscriptions: Optional[Subscriptions] = None):
        self._current_idx = None
        self._current_loop = None
        self.test_name = None
        self._atom_name = None
        self._bus = None
        self.ready = False

        if subscriptions:
            self._subscriptions = subscriptions
        else:
            self._subscriptions = Subscriptions()

        self.subscription_filters = None

    def handle_event(self, subj, testdata):
        if subj == message_subjects.TEST_FINISHED:
            if self._subscriptions.test_finished:
                self.event_test_finished(testdata)

        elif subj == message_subjects.TEST_RESULT:
            if self._subscriptions.test_result:
                self.event_test_result(testdata)

        elif subj == message_subjects.TEST_WARMUP:
            if self._subscriptions.test_warmup:
                self.event_test_warmup(testdata)

        elif subj == message_subjects.ATOM_EXECUTE:
            if self._subscriptions.actor_executed:
                self.event_atom_execute(testdata)

        elif subj == message_subjects.ACTOR_RESPONSE_RECEIVED:
            if self._subscriptions.actor_response_received:
                self.event_actor_response_received(testdata)

        elif subj == message_subjects.ATOM_FINISHED:
            self.event_atom_finished(testdata)
        elif subj == message_subjects.ATOM_WARMUP:
            self.event_atom_warmup(testdata)
        elif subj == message_subjects.ATOM_COLLECTING:
            self.event_atom_collecting(testdata)
        elif subj == message_subjects.ATOM_RESULT:
            self.event_atom_result(testdata)
        elif subj == message_subjects.RESULT_SUMMARY:
            self.event_result_summary(testdata)
        elif subj == message_subjects.LOOP_WARMUP:
            self.event_loop_warmup(testdata)
        elif subj == message_subjects.LOOP_FINISHED:
            self.event_loop_finished(testdata)
        elif subj == message_subjects.SENSOR_DATA:
            self.event_sensor_data(testdata)
        elif subj == message_subjects.TEST_FATAL:
            self.event_test_fatal(testdata)

    def event_test_finished(self, testdata):
        pass

    def event_test_result(self, testdata):
        pass

    def event_test_warmup(self, testdata):
        pass

    def event_atom_execute(self, testdata):
        pass

    def event_actor_response_received(self, testdata):
        pass

    def event_atom_finished(self, testdata):
        pass

    def event_atom_warmup(self, testdata: AtomWarmup):
        self._current_idx = testdata.idx.value
        self._current_loop = testdata.loop.value
        self._atom_name = testdata.atom_name.value

    def event_atom_collecting(self, testdata):
        pass

    def event_atom_result(self, testdata):
        pass

    def event_result_summary(self, testdata):
        pass

    def event_loop_warmup(self, testdata):
        pass

    def event_loop_finished(self, testdata):
        pass

    def event_sensor_data(self, testdata):
        pass

    def event_test_fatal(self, testdata):
        pass

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

    def get_subscriptions(self):
        """Return a tuple of tuples with each tuple
        containing and event name and the corresponding method
        to call when the event occurs.

        example:

        return (
            (subj.ATOM_WARMUP, self._atom_warmup_event),
            (subj.SENSOR_DATA, self._handle_sensor),
        )

        def _atom_warmup_event(self, subject, data: AtomData):
            pass
        """
        if self.subscription_filters:
            subs = (
                sub
                for sub in self.subscriptions
                if sub[0] in self.subscription_filters
            )

            return subs

        return self.subscriptions


class FileBasedDataHandler(BaseDataHandler):
    def __init__(
        self,
        report_name,
        output_path,
        subscriptions: Optional[Subscriptions] = None,
    ):
        """

        :param report_name: Optional name of the report.
            By default the name of the test is used.
        :param output_path: Path to store the report file.
            Can be relative or absolute.
        """
        super().__init__(subscriptions=subscriptions)
        self._filename = None
        self._report_name = report_name
        self._output_path = output_path
        self._report_data = []

    async def setup(self, test_name, bus):
        self._filename = create_report_file(
            test_name, self._report_name, self._output_path
        )

    async def shutdown(self, bus):
        self._flush()

    def _flush(self):
        """Writes buffer to file"""
        with open(self._filename, "a") as fl:
            fl.write("\n".join(self._report_data))
            fl.write("\n")
        # reset the summary
        self._report_data = []

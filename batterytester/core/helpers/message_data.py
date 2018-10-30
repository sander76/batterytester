import json
import typing
from collections import deque
from functools import singledispatch

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.constants import (
    KEY_ATOM_INDEX,
    KEY_ATOM_LOOP,
    KEY_ATOM_NAME,
    REASON,
)
from batterytester.core.helpers.helpers import get_current_timestamp
from batterytester.core.helpers.message_subjects import (
    PROCESS_STARTED,
    PROCESS_FINISHED,
    PROCESS_MESSAGE,
)

TYPE_STR = "str"
TYPE_TIME = "time"
TYPE_INT = "int"
TYPE_TIME_DELTA = "time_delta"
TYPE_JSON = "json"
TYPE_BOOL = "bool"
TYPE_STATUS = "status"
TYPE_STR_LIST = "strlist"

STATUS_RUNNING = "running"
STATUS_UNKOWN = "unknown"
STATUS_FINISHED = "finished"
STATUS_STARTING = "starting"

PROCESS_INFO = "process_info"


# todo: Add source to message. This can be used to later
# filter out messages depending on sender.


class Data:
    def __init__(self, value: typing.Any = "unknown", type_=TYPE_STR):
        self.value = value
        self.type = type_

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value and self.type == other.type

    def __ne__(self, other):
        return self.value != other.value or self.type != other.type


class ListData:
    def __init__(self):
        self._value = []
        self.type = TYPE_STR_LIST

    @property
    def value(self):
        return self._value

    def add(self, value):
        self._value.append(value)


class Message:
    def __init__(self):
        self.subj = "unknown"
        self.time = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.identity = None

    def to_json(self):
        return json.dumps(self, default=to_serializable)

    def to_dict(self):
        return json.loads(self.to_json())


class BaseEvent(Message):
    def __init__(self, subject, data=None):
        super().__init__()
        self.subj = subject
        if data:
            self.data = data
        else:
            self.data = {}


@singledispatch
def to_serializable(val):
    """Used by default"""
    return str(val)


@to_serializable.register(Data)
def data_serializable(val):
    return {"v": val.value, "type": val.type}


@to_serializable.register(ListData)
def data_serializable(val):
    return {"v": val.value, "type": val.type}


@to_serializable.register(deque)
def data_serializable(val):
    return list(val)


# @to_serializable.register(DeQueData)
# def data_serializable(val):
#     return {"v": list(val.value), "type": val.type}


@to_serializable.register(Message)
def message_serializable(val):
    _val = {}
    for key, data in vars(val).items():
        if data is not None:
            _val[key] = data
    _val["subj"] = val.subj
    return _val


class BaseProcessData(Message):
    identity = "process"
    process_name = None
    process_id = None
    status = None
    return_code = None
    message = None
    messages = None
    subj = subj.PROCESS_INFO

    def update(self, process_data):
        if process_data.status:
            self.status = process_data.status

        if process_data.process_name:
            self.process_name = process_data.process_name

        if process_data.process_id:
            self.process_id = process_data.process_id

        if process_data.message:
            self.message = process_data.message
            self.messages.append(process_data.message)

    @classmethod
    def base_process(cls, max_len=100):
        cl = cls()
        cl.subj = subj.PROCESS_INFO
        cl.messages = deque(maxlen=max_len)
        return cl

    @classmethod
    def process_started(cls, process_name, process_id):
        cl = cls()
        cl.subj = PROCESS_STARTED
        cl.status = STATUS_RUNNING
        cl.process_name = process_name
        cl.process_id = process_id
        return cl

    @classmethod
    def process_finished(cls, return_code):
        cl = cls()
        cl.subj = PROCESS_FINISHED
        cl.status = STATUS_FINISHED
        cl.return_code = return_code
        return cl

    @classmethod
    def process_message(cls, message):
        cl = cls()
        cl.subj = PROCESS_MESSAGE
        cl.message = message
        return cl


class BaseTestData(Message):
    def __init__(self):
        super().__init__()
        self.identity = "test_data"
        self.started = None
        self.test_name = None
        self.loop_count = None
        self.status = Data(STATUS_UNKOWN, TYPE_STATUS)
        self.time_finished = Data("unknown", type_=TYPE_TIME)
        self.reason = None


class TestWarmup(BaseTestData):
    def __init__(self, test_name, loop_count):
        super().__init__()
        self.subj = subj.TEST_WARMUP
        self.test_name = Data(test_name)
        self.started = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.loop_count = Data(loop_count, type_=TYPE_INT)
        self.status = Data("running")


class TestFinished(BaseTestData):
    def __init__(self):
        super().__init__()
        self.subj = subj.TEST_FINISHED
        self.status = Data(STATUS_FINISHED, TYPE_STATUS)
        self.time_finished = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.reason = Data(value="End of test reached.")


class TestFatal(TestFinished):
    def __init__(self, reason):
        super().__init__()
        self.subj = subj.TEST_FATAL
        self.reason = Data(value=str(reason))


class BaseLoopData(Message):
    def __init__(self):
        super().__init__()
        self.identity = "loop_data"
        self.atoms = None


class LoopWarmup(BaseLoopData):
    def __init__(self, atoms):
        super().__init__()
        self.subj = subj.LOOP_WARMUP
        self.duration = Data(
            value=sum((_atom.duration.value for _atom in atoms)), type_=TYPE_INT
        )
        self.atoms = atoms


class LoopFinished(BaseLoopData):
    def __init__(self):
        super().__init__()
        self.subj = subj.LOOP_FINISHED


class BaseAtomData(Message):
    def __init__(self):
        super().__init__()
        self.identity = "atom_data"
        self.atom_name = None
        self.idx = None
        self.loop = None
        self.status = None
        self.started = None
        self.duration = None
        self.reference_data = None


class AtomWarmup(BaseAtomData):
    def __init__(self, name, idx, loop, duration):
        super().__init__()
        self.atom_name = Data(name)
        self.subj = subj.ATOM_WARMUP
        self.idx = Data(idx)
        self.loop = Data(loop)
        self.status = Data()
        self.status_updated = Data()
        self.started = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.duration = Data(duration, type_=TYPE_TIME_DELTA)


class AtomExecute(BaseAtomData):
    def __init__(self, status):
        super().__init__()
        self.subj = subj.ATOM_EXECUTE
        self.status = Data(status)
        self.status_updated = Data(get_current_timestamp(), type_=TYPE_TIME)


class AtomCollecting(BaseAtomData):
    def __init__(self, status):
        super().__init__()
        self.status = Data(status)
        self.status_updated = Data(get_current_timestamp(), type_=TYPE_TIME)


class ActorResponse(Message):
    def __init__(self, response: dict):
        super().__init__()
        self.response = Data(response, type_=TYPE_JSON)


class AtomResult(Message):
    def __init__(self, passed: bool, reason: str = ""):
        super().__init__()
        self.passed = Data(passed)
        self.reason = Data(value=str(reason))


class TestSummary(Message):
    def __init__(self):
        super().__init__()
        self.subj = subj.RESULT_SUMMARY
        self.passed = Data(0, type_=TYPE_INT)
        self.failed = Data(0, type_=TYPE_INT)
        self.failed_ids = Data([], type_=TYPE_JSON)

    def atom_passed(self):
        self.passed.value += 1

    def atom_failed(self, idx, loop, test_name, reason):
        self.failed.value += 1
        self.failed_ids.value.append(
            {
                KEY_ATOM_INDEX: idx,
                KEY_ATOM_LOOP: loop,
                KEY_ATOM_NAME: test_name,
                REASON: reason,
            }
        )

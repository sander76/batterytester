import json
import typing
from functools import singledispatch
from typing import List

from batterytester.core.helpers.constants import KEY_ATOM_INDEX, \
    KEY_ATOM_LOOP, KEY_ATOM_NAME, REASON
from batterytester.core.helpers.helpers import get_current_timestamp
from batterytester.core.helpers.message_subjects import RESULT_SUMMARY

TYPE_STR = 'str'
TYPE_TIME = 'time'
TYPE_INT = 'int'
TYPE_TIME_DELTA = 'time_delta'
TYPE_JSON = 'json'
TYPE_BOOL = 'bool'
TYPE_STATUS = 'status'

STATUS_RUNNING = 'running'
STATUS_UNKOWN = 'unknown'
STATUS_FINISHED = 'finished'


class Data:
    def __init__(self, value: typing.Any = 'unknown', type_=TYPE_STR):
        self.value = value
        self.type = type_


class Message:
    def __init__(self):
        self.subj = ''
        self.cache = False

    def to_json(self):
        return json.dumps(self, default=to_serializable)


@singledispatch
def to_serializable(val):
    """Used by default"""
    return str(val)


@to_serializable.register(Data)
def data_serializable(val):
    return {"v": val.value, "type": val.type}


@to_serializable.register(Message)
def message_serializable(val):
    return vars(val)


class BaseTestData(Message):
    def __init__(self):
        super().__init__()
        self.time_finished = Data("unknown", type_=TYPE_TIME)
        self.status = Data("unknown")


class ProcessData(Message):
    def __init__(self, process_id):
        super().__init__()
        self.process_id = Data(process_id, TYPE_INT)
        self.status = Data(STATUS_RUNNING, TYPE_STATUS)
        self.messages = []

    def update(self, status=None, message=None):
        if status:
            self.status = Data(status, TYPE_STATUS)
        if message:
            self.messages.append(message)


class TestFinished(BaseTestData):
    def __init__(self):
        super().__init__()
        # todo: add total runtime.
        self.status = Data(STATUS_FINISHED, TYPE_STATUS)
        self.time_finished = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.reason = Data(value='End of test reached.')


class FatalData(TestFinished):
    def __init__(self, reason):
        super().__init__()
        self.reason = Data(value=reason)


class TestData(BaseTestData):
    def __init__(self, test_name, loop_count):
        super().__init__()
        self.test_name = Data(test_name)
        self.started = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.loop_count = Data(loop_count, type_=TYPE_INT)
        self.status = Data("running")


class AtomData(Message):
    def __init__(self, name, idx, loop, duration):
        super().__init__()
        self.atom_name = Data(name)
        self.idx = Data(idx)
        self.loop = Data(loop)
        self.status = Data()
        self.status_updated = Data()
        self.started = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.duration = Data(duration, type_=TYPE_TIME_DELTA)


class LoopData(BaseTestData):
    def __init__(self, atoms: List[AtomData]):
        super().__init__()
        self.atoms = atoms


class AtomStatus(Message):
    def __init__(self, status):
        super().__init__()
        self.status = Data(status)
        self.status_updated = Data(get_current_timestamp(), type_=TYPE_TIME)


class AtomResult(Message):
    def __init__(self, passed: bool, reason=''):
        super().__init__()
        self.passed = Data(passed)
        self.reason = Data(reason)


class TestSummary(Message):
    def __init__(self):
        super().__init__()
        self.subj = RESULT_SUMMARY
        self.passed = Data(0, type_=TYPE_INT)
        self.failed = Data(0, type_=TYPE_INT)
        self.failed_ids = Data([], type_=TYPE_JSON)

    def atom_passed(self):
        self.passed.value += 1

    def atom_failed(self, idx, loop, test_name, reason):
        self.failed.value += 1
        self.failed_ids.value.append({
            KEY_ATOM_INDEX: idx,
            KEY_ATOM_LOOP: loop,
            KEY_ATOM_NAME: test_name,
            REASON: reason
        })

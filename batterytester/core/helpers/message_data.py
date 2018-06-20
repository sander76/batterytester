import json
import typing
from functools import singledispatch
from typing import List

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.constants import KEY_ATOM_INDEX, \
    KEY_ATOM_LOOP, KEY_ATOM_NAME, REASON
from batterytester.core.helpers.helpers import get_current_timestamp

# from batterytester.core.helpers.message_subjects import RESULT_SUMMARY, \
#     PROCESS_INFO

TYPE_STR = 'str'
TYPE_TIME = 'time'
TYPE_INT = 'int'
TYPE_TIME_DELTA = 'time_delta'
TYPE_JSON = 'json'
TYPE_BOOL = 'bool'
TYPE_STATUS = 'status'
TYPE_STR_LIST = 'strlist'

STATUS_RUNNING = 'running'
STATUS_UNKOWN = 'unknown'
STATUS_FINISHED = 'finished'
STATUS_STARTING = 'starting'


# todo: Add source to message. This can be used to later filter out messages depending on sender.

class Data:
    def __init__(self, value: typing.Any = 'unknown', type_=TYPE_STR):
        self.value = value
        self.type = type_

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (
                    self.value == other.value and
                    self.type == other.type
            )

    def __ne__(self, other):
        return (
                self.value != other.value or
                self.type != other.type
        )


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
        self.subj = 'unknown'
        self.time = Data(get_current_timestamp(), type_=TYPE_TIME)

    def to_json(self):
        return json.dumps(self, default=to_serializable)

    def to_dict(self):
        return json.loads(self.to_json())


@singledispatch
def to_serializable(val):
    """Used by default"""
    return str(val)


@to_serializable.register(Data)
def data_serializable(val):
    return {"v": val.value, "type": val.type}


@to_serializable.register(ListData)
def data_serializable(val):
    return {'v': val.value, 'type': val.type}


@to_serializable.register(Message)
def message_serializable(val):
    _val = vars(val)
    _val['subj'] = val.subj
    return _val


class BaseTestData(Message):
    def __init__(self):
        super().__init__()
        self.time_finished = Data("unknown", type_=TYPE_TIME)
        self.status = Data(STATUS_UNKOWN, TYPE_STATUS)


class ProcessData(Message):

    def __init__(self):
        super().__init__()
        self.subj = subj.PROCESS_INFO
        self._process_name = Data()
        self._process_id = Data(type_=TYPE_INT)
        self._status = Data(STATUS_UNKOWN, TYPE_STATUS)
        self._return_code = Data(type_=TYPE_INT)
        self._messages = ListData()

    @property
    def process_name(self):
        return self._process_name.value

    @process_name.setter
    def process_name(self, value):
        self._process_name.value = value

    @property
    def process_id(self):
        return self._process_id.value

    @process_id.setter
    def process_id(self, value):
        self._process_id.value = value

    @property
    def status(self):
        return self._status.value

    @status.setter
    def status(self, value):
        self._status.value = value

    @property
    def return_code(self):
        return self._return_code.value

    @return_code.setter
    def return_code(self, value):
        self._return_code.value = value

    def add_message(self, message: str):
        self._messages.add(message)


class TestFinished(BaseTestData):
    def __init__(self):
        super().__init__()
        self.subj = subj.TEST_FINISHED
        self.status = Data(STATUS_FINISHED, TYPE_STATUS)
        self.time_finished = Data(get_current_timestamp(), type_=TYPE_TIME)
        self.reason = Data(value='End of test reached.')


class FatalData(TestFinished):
    def __init__(self, reason):
        super().__init__()
        self.subj = subj.TEST_FATAL
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


class LoopFinished(Message):
    def __init__(self):
        super().__init__()
        self.subj = subj.LOOP_FINISHED


class AtomStatus(Message):
    def __init__(self, status):
        super().__init__()
        self.status = Data(status)
        self.status_updated = Data(get_current_timestamp(), type_=TYPE_TIME)


class ActorResponse(Message):
    def __init__(self, response: dict):
        super().__init__()
        self.response = Data(response, type_=TYPE_JSON)


class AtomResult(Message):
    def __init__(self, passed: bool, reason: str = ''):
        super().__init__()
        self.passed = Data(passed)
        self.reason = Data(reason)


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
        self.failed_ids.value.append({
            KEY_ATOM_INDEX: idx,
            KEY_ATOM_LOOP: loop,
            KEY_ATOM_NAME: test_name,
            REASON: reason
        })

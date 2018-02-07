from functools import singledispatch

from batterytester.core.helpers.constants import KEY_ATOM_INDEX, \
    KEY_ATOM_LOOP, KEY_ATOM_NAME, REASON
from batterytester.core.helpers.helpers import get_current_timestamp


# todo: all properties should go in a list when serializing to manage the order of appearance.


class Data:
    def __init__(self, value='unknown', type='str'):
        self.value = value
        self.type = type


class Message:
    def __init__(self):
        self.subj = ''


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


class FatalData(Message):
    def __init__(self, reason):
        super().__init__()
        self.reason = Data(value=reason)


class BaseTestData(Message):
    def __init__(self):
        super().__init__()
        self.time_finished = Data("unknown")
        self.status = Data("unknown")


class TestFinished(BaseTestData):
    def __init__(self):
        super().__init__()
        self.status = "finished"
        self.time_finished = Data(get_current_timestamp())


class TestData(BaseTestData):
    def __init__(self, test_name, loop_count):
        super().__init__()
        self.test_name = Data(test_name)
        self.started = Data(get_current_timestamp())
        self.loop_count = Data(loop_count)
        self.status = Data("running")


class AtomData(Message):
    def __init__(self, name, idx, loop, duration):
        super().__init__()
        self.atom_name = Data(name)
        self.idx = Data(idx)
        self.loop = Data(loop)
        self.status = Data()
        self.status_updated = Data()
        self.started = Data(get_current_timestamp())
        self.duration = Data(duration)


class AtomStatus(Message):
    def __init__(self, status):
        super().__init__()
        self.status = Data(status)
        self.status_updated = Data(get_current_timestamp())


class AtomResult(Message):
    def __init__(self, passed: bool, reason=''):
        super().__init__()
        self.passed = Data(passed)
        self.reason = Data(reason)


class TestSummary(Message):
    def __init__(self):
        super().__init__()
        self.passed = Data(0)
        self.failed = Data(0)
        self.failed_ids = Data([])

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

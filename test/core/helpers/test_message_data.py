import json

from batterytester.core.helpers.message_data import (
    Data,
    to_serializable,
    TestFatal,
    Message,
    ProcessData,
    STATUS_RUNNING,
)
from batterytester.core.helpers.message_subjects import PROCESS_INFO
from core.helpers.message_data import TestFinished, DeQueData


def test_simple():
    m = Data(value=1)
    _js = json.dumps(m, default=to_serializable)
    _dict = json.loads(_js)
    assert _dict == {"v": 1, "type": "str"}


def test_internal_to_json():
    m = Message()
    _js = m.to_json()
    _dict = json.loads(_js)
    assert "subj" in _dict
    assert "time" in _dict


def test_fatal():
    fatal = TestFatal("no idea")
    _js = json.dumps(fatal, default=to_serializable)
    _dict = json.loads(_js)
    assert _dict["reason"]["v"] == "no idea"
    _js = fatal.to_json()
    _dict = json.loads(_js)
    assert _dict["reason"]["v"] == "no idea"
    _dct = fatal.to_dict()
    assert _dct["reason"]["v"] == "no idea"


def test_process_data():
    process_name = "test_process"
    process = ProcessData()
    process.process_name = process_name
    _js = process.to_json()
    _dict = json.loads(_js)
    assert _dict["_process_name"]["v"] == process_name


def test_process_data_to_dict():
    process = ProcessData()
    process.process_name = "test_name"
    process.process_id = 123344
    process.return_code = 1234
    process.status = STATUS_RUNNING
    process.subj = PROCESS_INFO
    process.add_message("testing testing")
    a = process.to_dict()
    pass


def test_test_finished():
    finished = TestFinished()
    _dict = finished.to_dict()
    _js = finished.to_json()
    assert "test_name" not in _dict
    assert "test_name" not in _js


def test_dequedata():
    data = DeQueData(max_len=5)
    for val in range(10):
        data.add(val)

    assert len(data) == 5
    assert data._value[0] == 5
    assert data._value[-1] == 9

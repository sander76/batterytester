import json

from batterytester.core.helpers.message_data import (
    Data,
    to_serializable,
    TestFatal,
    Message,

)
from core.helpers.message_data import TestFinished, BaseProcessData


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
    baseprocess = BaseProcessData.process_started(process_name, 123)
    _js = baseprocess.to_json()
    _dict = json.loads(_js)
    assert _dict["process_name"] == process_name


def test_test_finished():
    finished = TestFinished()
    _dict = finished.to_dict()
    _js = finished.to_json()
    assert "test_name" not in _dict
    assert "test_name" not in _js



def test_dequedata_json():
    message = BaseProcessData.base_process(max_len=3)
    js = message.to_json()
    dct = json.loads(js)
    assert isinstance(dct["messages"],list)


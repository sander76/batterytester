import json

from batterytester.core.helpers.message_data import Data, to_serializable, \
    FatalData, Message


def test_simple():
    m = Data(value=1)
    _js = json.dumps(m, default=to_serializable)
    _dict = json.loads(_js)
    assert _dict == {"v": 1, "type": "str"}


def test_internal_to_json():
    m = Message()
    _js = m.to_json()
    _dict = json.loads(_js)
    assert _dict == {'subj': '', 'cache': False}


def test_fatal():
    fatal = FatalData("no idea")
    _js = json.dumps(fatal, default=to_serializable)
    _dict = json.loads(_js)
    assert _dict['reason']['v'] == 'no idea'
    _js = fatal.to_json()
    _dict = json.loads(_js)
    assert _dict['reason']['v'] == 'no idea'

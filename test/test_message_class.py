import json

from batterytester.core.helpers.message_data import Data, to_serializable, \
    FatalData


def test_simple():
    m = Data(value=1)
    _js = json.dumps(m, default=to_serializable)
    _dict = json.loads(_js)
    assert _dict == {"v": 1, "type": "str"}


def test_fatal():
    fatal = FatalData("no idea")
    _js = json.dumps(fatal, default=to_serializable)
    _dict = json.loads(_js)
    assert _dict['reason']['v'] == 'no idea'

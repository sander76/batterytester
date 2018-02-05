from batterytester.core.datahandlers.influx import line_protocol_tags


def test_line_protocol_tags():
    _in = {'a': 1, 'b': 2}
    _out = line_protocol_tags(_in)
    assert _out == ',a=1,b=2'


def test_empty_time_protocol_tags():
    _in = {}
    _out = line_protocol_tags(_in)
    assert _out == ''


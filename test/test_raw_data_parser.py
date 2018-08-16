import pytest

from batterytester.components.sensor.incoming_parser.raw_data_parser import \
    RawDataParser
from batterytester.core.helpers.constants import ATTR_SENSOR_NAME


def test_parser():
    parser = RawDataParser(None,'abc/abc')

    _coming = b'{i:a:1}'
    val = parser._interpret(_coming)
    assert val[ATTR_SENSOR_NAME] == 'abc-abc'
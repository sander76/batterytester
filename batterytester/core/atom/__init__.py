"""Individual test being performed"""
import logging
import os

LOGGING = logging.getLogger(__name__)
SENSOR_FILE_FORMAT = 'loop_{}-idx_{}.json'


def get_sensor_data_name(save_location, test_sequence_number,
                         current_loop=0):
    _fname = os.path.join(
        save_location, SENSOR_FILE_FORMAT.format(
            current_loop, test_sequence_number))
    LOGGING.debug("saving data to %s" % _fname)
    return _fname


def find_reference_data(idx, location):
    _search = SENSOR_FILE_FORMAT.format(0, idx)

    for _file in os.listdir(location):
        if _file == _search:
            return _file
    return None


class RefGetter:
    def __init__(self, key, attribute=None):
        self._key = key
        self._attribute = attribute

    def get_ref(self, results):
        _ref = results[self._key]
        if self._attribute is None:
            return _ref
        if isinstance(_ref, dict):
            return _ref[self._attribute]
        else:
            _val = getattr(_ref, self._attribute)
            return _val

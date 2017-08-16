import json

from batterytester.constants import ATTR_DATABASE, ATTR_SENSOR_DATA_PARSER, \
    ATTR_SENSOR_DATA_CONNECTOR, ATTR_MAIN_TEST, ATTR_ARGS
from batterytester.mylogger.mylogger import setup_logging
from batterytester.start import get_platform, process_config

if __name__ == "__main__":
    setup_logging(default_path='batterytester/mylogger/debug_logging.json')

    test = process_config("config_sequence_reference_test.json")

    print(test.bus.start_test())
    print("finished test.")


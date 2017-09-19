"""
Entrypoint for setting up a test
takes a json config file and initializes the correct instances.

"""

import importlib
import json

from batterytester.helpers.constants import ATTR_SENSOR_DATA_CONNECTOR, \
    ATTR_DATABASE, \
    ATTR_PLATFORM, ATTR_ARGS, ATTR_SENSOR_DATA_PARSER, ATTR_MAIN_TEST


def _instantiate(key):
    _args = key.get(ATTR_ARGS)
    _platform = key.get(ATTR_PLATFORM)

    _parts = _platform.split('.')
    _module = '.'.join(_parts[:-1])
    _class = _parts[-1]

    _module = importlib.import_module(_module)

    if _args:
        _instance = getattr(_module,_class)(**_args)
    else:
        _instance = getattr(_module,_class)()
    return _instance



def get_platform(config,platform_key):
    _platform = config.get(platform_key)
    _cls = _instantiate(_platform)
    return _cls

def process_config(config_file):
    with open(config_file, 'r') as fl:
        config = json.loads(fl.read())

    data_parser = get_platform(config, ATTR_SENSOR_DATA_PARSER)

    config[ATTR_SENSOR_DATA_CONNECTOR][ATTR_ARGS][
        ATTR_SENSOR_DATA_PARSER] = data_parser
    connector = get_platform(config, ATTR_SENSOR_DATA_CONNECTOR)

    database = get_platform(config, ATTR_DATABASE)

    if ATTR_ARGS in config[ATTR_MAIN_TEST]:
        config[ATTR_MAIN_TEST][ATTR_ARGS][ATTR_DATABASE] = database
    else:
        config[ATTR_MAIN_TEST][ATTR_ARGS] = {ATTR_DATABASE: database}

    config[ATTR_MAIN_TEST][ATTR_ARGS][ATTR_SENSOR_DATA_CONNECTOR] = connector
    main_test = get_platform(config, ATTR_MAIN_TEST)
    return main_test

# if __name__ == "__main__":
#     with open("obsolete_config.json", 'r') as fl:
#         _js = json.loads(fl.read())
#     _test = _js['test']
#
#     set_connector(_test)
#     set_database(_test)
#
#     test = importlib.import_module(_test['main_test']).setup(_test['args'])
#     test.bus.start_test()

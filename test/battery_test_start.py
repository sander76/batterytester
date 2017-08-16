import importlib
import json


def set_connector(test):
    _key = "sensor_data_connector"
    _sensor_data_connector = test[_key]
    _connector = importlib.import_module(_sensor_data_connector['class'])
    test[_key] = _connector.setup(_sensor_data_connector['args'])


def set_database(test):
    _key = "database"
    _database = test[_key]
    _database_module = importlib.import_module(_database["class"])
    database = _database_module.setup(_database["args"])
    test[_key] = database


if __name__ == "__main__":
    with open("obsolete_config.json", 'r') as fl:
        _js = json.loads(fl.read())
    _test = _js['test']


    set_connector(_test)
    set_database(_test)

    test = importlib.import_module(_test['main_test']).setup(_test['args'])
    test.bus.start_test()

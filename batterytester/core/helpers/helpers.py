import datetime
import json
import logging
import logging.config
import os
from time import time, strftime, localtime

LOOP_TIME_OUT = 2

_LOGGER = logging.getLogger(__name__)

TIME_FORMAT = "%Y-%m-%d_%H-%M-%S"


def get_current_time():
    return datetime.datetime.now().replace(microsecond=0)


def get_current_timestamp():
    """Returns the time in seconds since the epoch"""
    return time()


def get_time_string(datetime_obj: datetime.datetime):
    return datetime_obj.strftime(TIME_FORMAT)


def get_localtime_string(timestamp):
    return strftime(TIME_FORMAT, localtime(timestamp))


def get_current_time_string():
    return get_current_time().strftime(TIME_FORMAT)


class NonFatalTestFailException(Exception):
    pass


class FatalTestFailException(Exception):
    pass

class StopTestException(FatalTestFailException):
    pass

class SquidConnectException(FatalTestFailException):
    pass


class AtomExecuteError(Exception):
    pass


class TestSetupException(Exception):
    pass


def check_output_location(test_location):
    if os.path.exists(test_location):
        files = os.listdir(test_location)
        if files:
            print("TEST LOCATION ALREADY CONTAINS FILES:")
            print(test_location)
            print("IF PROCEED ALL CONTAINING DATA WILL BE ERASED.")
            proceed = input("PROCEED ? [y/n] >")
            if proceed == "y":
                # clear all files in folder.
                for _fl in files:
                    os.remove(os.path.join(test_location, _fl))
                return True
            else:
                return False
    if not os.path.exists(test_location):
        os.makedirs(test_location)
    return True


def load_config_file(config_file: str) -> dict:
    """Load config dict from json file.

    :param config_file: full path to the json file.
    :return: a dict.
    """

    with open(config_file, "r") as fl:
        dct = json.load(fl)
    return dct


def set_test_config(config_file: str):
    """Load logging config from json file.

    :param config_file: full path to the json file.
    """
    dct = load_config_file(config_file)

    logging.config.dictConfig(dct["test_logging"])

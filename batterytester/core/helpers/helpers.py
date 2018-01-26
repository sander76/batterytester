import os

import logging

import datetime

LOOP_TIME_OUT = 2

_LOGGER = logging.getLogger(__name__)


def get_current_time():
    return datetime.datetime.now().replace(microsecond=0)


def get_time_string(datetime_obj: datetime.datetime):
    return datetime_obj.strftime('%Y-%m-%d_%H-%M-%S')


def get_current_time_string():
    return get_current_time().strftime('%Y-%m-%d_%H-%M-%S')


# def slugify(text: str) -> str:
#     """Slugify a given text."""
#     text = normalize('NFKD', text)
#     text = text.lower()
#     text = text.replace(" ", "_")
#     text = text.translate(TBL_SLUGIFY)
#     text = RE_SLUGIFY.sub("", text)
#
#     return text


class TestFailException(Exception):
    pass


def check_output_location(test_location):
    if os.path.exists(test_location):
        files = os.listdir(test_location)
        if files:
            print("TEST LOCATION ALREADY CONTAINS FILES:")
            print(test_location)
            print("IF PROCEED ALL CONTAINING DATA WILL BE ERASED.")
            proceed = input("PROCEED ? [y/n] >")
            if proceed == 'y':
                # clear all files in folder.
                for _fl in files:
                    os.remove(os.path.join(test_location, _fl))
                return True
            else:
                return False
    if not os.path.exists(test_location):
        os.makedirs(test_location)
    return True

# Measurement = namedtuple('Measurement', ['values', 'timestamp'])
# #todo: convert this to a dict ?

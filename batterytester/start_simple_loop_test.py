import importlib
from argparse import ArgumentParser

from batterytester.helpers.helpers import check_output_location
from batterytester.main_test.loop_test import LoopTest

parser = ArgumentParser()
parser.add_argument('configuration')


def start_test(config):
    if check_output_location(config.test_location):
        sequence_test = LoopTest(
            config)
        sequence_test.bus.start_test()


if __name__ == "__main__":
    # instantiate the config class.
    args = parser.parse_args()
    _module = args.configuration
    mymodule = importlib.import_module(_module)
    _config = getattr(mymodule, 'TestConfig')
    if _config:
        config = _config()

        start_test(config)

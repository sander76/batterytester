from batterytester.helpers.base_config import BaseConfig
from batterytester.helpers.helpers import check_output_location
from batterytester.main_test.loop_test import LoopTest


class LoopTestConfig(BaseConfig):
    def __init__(self):
        super().__init__()

    def start_test(self, add_time_stamp_to_report=True):
        super().start_test(add_time_stamp_to_report)
        if check_output_location(self.test_location):
            sequence_test = LoopTest(self)
            sequence_test.bus.start_test()

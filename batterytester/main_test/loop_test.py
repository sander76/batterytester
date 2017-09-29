from batterytester.bus import Bus
from batterytester.main_test import BaseTest


class LoopTest(BaseTest):
    def __init__(self, test_name: str, loop_count: int,
                 delay: int, test_location,telegram_token):
        bus = Bus()
        self.delay = delay
        super().__init__(
            test_name,
            loop_count=loop_count,
            bus=bus,
            sensor_data_connector=None,
            database=None,
            test_location=test_location
        )

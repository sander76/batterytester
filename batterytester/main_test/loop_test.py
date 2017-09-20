from batterytester.helpers.base_config import BaseConfig
from batterytester.main_test import BaseTest

class LoopTest(BaseTest):
    def __init__(self, config: BaseConfig):
        super().__init__(
            config,
            sensor_data_connector=None,
            database=None
        )

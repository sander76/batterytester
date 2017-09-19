from batterytester.helpers.base_config import BaseConfig
from batterytester.main_test import BaseTest
from batterytester.test_atom import TestAtom


class LoopTest(BaseTest):
    def __init__(self, config: BaseConfig):
        super().__init__(
            config,
            sensor_data_connector=None,
            database=None
        )

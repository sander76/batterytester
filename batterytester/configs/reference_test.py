from batterytester.connector.async_serial_connector import AsyncSerialConnector
from batterytester.main_test import BaseReferenceTest

test = BaseReferenceTest(
    test_name='ref_test',
    loop_count=2,
    learning_mode=True,
    sensor_data_connector=AsyncSerialConnector()


)

if __name__=="__main__":
    test.start_test()

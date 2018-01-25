# from batterytester.connector.async_serial_connector import AsyncSerialConnector
# from batterytester.incoming_parser.sequence_data_parser import \
#     SequenceDataParser
# from batterytester.main_test import BaseReferenceTest
#
#
# class PowerViewEncoderReferenceTest(BaseReferenceTest):
#     def __init__(self,
#                  test_name: str,
#                  loop_count: int,
#                  learning_mode,
#                  test_location: str = None,
#                  reference_test_location: str = None,
#                  telegram_token=None,
#                  telegram_chat_id=None
#                  ):
#         super().__init__(
#             test_name,
#             loop_count,
#             learning_mode=learning_mode,
#             test_location=test_location,
#             reference_test_location=reference_test_location,
#             telegram_token=telegram_token,
#             telegram_chat_id=telegram_chat_id
#         )
#         _sensor_data_parser = binary
#         self.sensor_data_connector = AsyncSerialConnector(self.bus, SequenceDataParser, )

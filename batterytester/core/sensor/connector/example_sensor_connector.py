# """An example incoming sensor data source.
#
# Randomly generates data every 5 seconds and puts it into the sensor_data_queue.
# """
#
# import asyncio
# import logging
# import random
# import string
# from asyncio.futures import CancelledError
#
# from batterytester.core.bus import Bus
# from batterytester.core.sensor.connector import AsyncSensorConnector
#
# _LOGGER = logging.getLogger(__name__)
#
#
# class ExampleSensorConnector(AsyncSensorConnector):
#     def __init__(self, sensor_data_parser, bus: Bus):
#         AsyncSensorConnector.__init__(self, sensor_data_parser,bus)
#
#     @asyncio.coroutine
#     def async_listen_for_data(self):
#         """Method to generate random data and pushing it to the
#         process_incoming method."""
#         try:
#             while True:
#                 gen = ''.join(
#                     random.choice(
#                         string.ascii_lowercase)
#                     for _ in range(10))
#                 self.bus.add_async_task(self.process_incoming(gen))
#                 yield from asyncio.sleep(0.1)
#         except CancelledError:
#             return

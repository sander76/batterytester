# import logging
#
# import time
#
# import asyncio
# from asyncio.futures import CancelledError
#
# from serial.serialutil import SerialException
#
# from batterytester.core.base_connectors import AsyncSensorConnector, \
#     ThreadedSensorConnector
# from batterytester.helpers import LOOP_TIME_OUT, Bus
# from batterytester.incoming_parser import IncomingParser
import logging
from serial import Serial, SerialException

#
LOGGER = logging.getLogger(__name__)
#
#

from batterytester.core.sensor.connector import ThreadedSensorConnector


class ThreadedSerialSensorConnector(ThreadedSensorConnector):
    def __init__(
            self,
            bus,
            serial_port,
            serial_speed,
            try_delay=10):
        super().__init__(bus)
        self.s = Serial()
        self.serial_port = serial_port
        self.s.port = serial_port
        self.s.baudrate = serial_speed
        self.trydelay = try_delay

    def connect(self):
        try:
            LOGGER.debug(
                "Connecting to serial port {}.".format(self.serial_port))
            self.s.open()
        except SerialException as err:

            LOGGER.exception(err)
            self.bus.stop_test()
        except Exception as err:
            LOGGER.exception(err)

    def stop(self):
        self.s.close()

    def listen_for_data(self):
        while self.bus.running:
            try:
                data = self.s.read(self.s.in_waiting or 1)
                self.bus.loop.call_soon_threadsafe(
                    self.raw_sensor_data_queue.put_nowait,data)
            except SerialException:
                LOGGER.error("error reading from serial port")
                break
        LOGGER.debug("exiting serial loop")

    def _write_to_arduino(self, upstring):
        self.s.write(upstring)

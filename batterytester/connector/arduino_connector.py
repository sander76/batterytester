import logging

import time

import asyncio
from asyncio.futures import CancelledError

from serial.serialutil import SerialException

from batterytester.connector import ThreadedSensorConnector, \
    AsyncSensorConnector
from batterytester.helpers import LOOP_TIME_OUT, Bus
from batterytester.incoming_parser import IncomingParser
from serial import Serial

lgr = logging.getLogger(__name__)


class AsyncioArduinoConnector(AsyncSensorConnector):
    def __init__(
            self,
            bus: Bus,
            sensor_data_parser: IncomingParser,
            serial_port,
            serial_speed):
        AsyncSensorConnector.__init__(self, sensor_data_parser, bus)
        # setting timeout at zero. This makes the read method non-blocking.
        self.s = Serial(
            port=serial_port,
            baudrate=serial_speed,
            timeout=0
        )

    @asyncio.coroutine
    def async_listen_for_data(self, *args):
        """Long running task.
        Listens for incoming raw data and puts it into the
        raw_sensor_data_queue
        """
        try:
            while True:
                # Non blocking read.
                _data = self.s.read(self.s.in_waiting)
                yield from self.raw_sensor_data_queue.put(_data)
                # print(str(_data))
                yield from asyncio.sleep(0.5)
        except SerialException as e:
            lgr.exception(e)
            self.s.close()
            self.bus.stop_test('Error reading from serial port.')
        except CancelledError:
            self.s.close()
            lgr.info("Stopped Serial connector")


class ArduinoConnector(ThreadedSensorConnector):
    def __init__(
            self,
            sensor_data_parser: IncomingParser,
            serial_port,
            serial_speed,
            try_delay=10):
        ThreadedSensorConnector.__init__(
            self,
            sensor_data_parser)
        self.s = Serial()
        self.s.timeout = LOOP_TIME_OUT
        self.serial_port = serial_port
        self.s.port = serial_port
        self.s.baudrate = serial_speed
        self.trydelay = try_delay

    def connect(self):
        try:
            lgr.debug("Connecting to serial port {}.".format(self.serial_port))
            self.s.open()
        except SerialException:
            lgr.info("serial port opening problem.")
            self.bus.stop_test()

    def stop(self):
        self.s.close()

    def listen_for_data(self):
        while self.bus.running:
            try:
                data = self.s.read(self.s.in_waiting or 1)
                self.bus.loop.call_soon_threadsafe(self.process_incoming,
                                                   data)
            except SerialException:
                lgr.error("error reading from serial port")
                time.sleep(1)
                break
        lgr.debug("exiting serial loop")

    def _write_to_arduino(self, upstring):
        self.s.write(upstring)

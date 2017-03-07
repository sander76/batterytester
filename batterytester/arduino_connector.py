import asyncio

import time
from threading import Thread

from serial import Serial
from serial.serialutil import SerialException

import logging

from batterytester.helpers import get_bus, LOOP_TIME_OUT
from batterytester.incoming_parser import IncomingParser

lgr = logging.getLogger(__name__)


class SensorConnector:
    def __init__(
            self,
            sensor_data_parser: IncomingParser,
    ):
        self.bus = get_bus()
        self.sensor_data_queue = asyncio.Queue(loop=self.bus.loop)
        self.sensor_data_parser = sensor_data_parser

    @asyncio.coroutine
    def process_incoming(self, raw_incoming):
        for data in self.sensor_data_parser.process(raw_incoming):
            yield from self.sensor_data_queue.put(data)


class AsyncSensorConnector(SensorConnector):
    def __init__(
            self,
            sensor_data_parser: IncomingParser):
        SensorConnector.__init__(
            self,
            sensor_data_parser)
        #self.bus.add_async_task(self.async_list_for_data())
        self.bus.add_task

    def start(self):
        pass

    def finished(self):
        pass

    def stop(self):
        pass

    @asyncio.coroutine
    def async_list_for_data(self):
        return


class ThreadedSensorConnector(SensorConnector):
    def __init__(
            self,
            sensor_data_parser: IncomingParser):
        SensorConnector.__init__(
            self,
            sensor_data_parser)
        self.t = Thread(target=self.listen_for_data)
        self.bus.add_threaded_task(self.t)
        self.bus.add_callback(self.connect)

    def connect(self):
        pass

    def disconnect(self):
        pass

    def listen_for_data(self):
        """Method to be run inside a separate thread continuously checking
                incoming data. When incoming data is captured it is sent
                back to the main event loop."""
        return


class ArduinoConnector(ThreadedSensorConnector):
    def __init__(
            self,
            sensor_data_parser: IncomingParser,
            sensor_data_queue,
            serial_port,
            serial_speed,
            try_delay=10):
        SensorConnector.__init__(
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

    def disconnect(self):
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

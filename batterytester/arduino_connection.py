import asyncio
import concurrent
from serial import Serial
from serial.serialutil import SerialException

import logging

lgr = logging.getLogger(__name__)


# def byte_to_string_rep(byte_instance):
#     string_rep = []
#     for bt in byte_instance:
#
#         if bt >= 32 and bt < 127:
#             string_rep.append(chr(bt))
#         else:
#             string_rep.append(hex(bt))
#     _string_rep = ''.join(string_rep)
#     return _string_rep


class ArduinoConnection:
    def __init__(self, loop, serial_port, serial_speed, try_delay=10):
        # self.network_id = b'\x00\x03I' + network_id
        self.s = Serial()
        self.s.timeout = 10
        self.serial_port = serial_port
        self.s.port = serial_port
        self.s.baudrate = serial_speed
        self.trydelay = try_delay
        self.loop = loop
        self.connect()

    # handler
    def connect(self):
        try:
            lgr.debug("Connecting to serial port {}.".format(self.serial_port))
            self.s.open()
        except SerialException:
            lgr.info("serial port opening problem.")
            self.loop.stop()

    # the method which gets wrapped in the asyncio thread executor.
    def get_byte(self, event):
        if event.is_set():
            return
        if self.s.is_open:
            try:
                data = self.s.readline()
                data = data.rstrip(b'\n')
                return data
            except SerialException as e:
                lgr.exception(e)

    # Runs blocking function in executor, yielding the result
    @asyncio.coroutine
    def get_byte_async(self, event):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            res = yield from self.loop.run_in_executor(executor, self.get_byte,
                                                       event)
            return res

    def _write_to_arduino(self, upstring):
        self.s.write(upstring)

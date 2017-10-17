import asyncio
import logging
from asyncio.futures import CancelledError

from serial import Serial
from serial.serialutil import SerialException

from batterytester.bus import Bus
from batterytester.connector import AsyncSensorConnector
from batterytester.incoming_parser import IncomingParser

lgr = logging.getLogger(__name__)

class AsyncSerialConnector(AsyncSensorConnector):
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
                yield from asyncio.sleep(0.5)
        except SerialException as e:
            lgr.exception(e)
            self.s.close()
            self.bus.stop_test('Error reading from serial port.')
        except CancelledError:
            self.s.close()
            lgr.info("Stopped Serial connector")
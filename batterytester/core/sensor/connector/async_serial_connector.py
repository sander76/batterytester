import asyncio
import logging

from asyncio.futures import CancelledError
from serial import Serial
from serial.serialutil import SerialException
from batterytester.core.bus import Bus
from batterytester.core.sensor.connector import AsyncSensorConnector

lgr = logging.getLogger(__name__)


class AsyncSerialConnector(AsyncSensorConnector):
    def __init__(
            self,
            bus: Bus,
            serial_port,
            serial_speed,
            read_delay=1
    ):
        super().__init__(bus)
        # setting timeout at zero. This makes the read method non-blocking.
        self.s = Serial(
            port=serial_port,
            baudrate=serial_speed,
            timeout=0
        )
        self.read_delay = read_delay

    @asyncio.coroutine
    def async_listen_for_data(self, *args):
        """Long running task inside a separate thread.

        Listens for incoming raw data and puts it into the
        raw_sensor_data_queue
        """
        try:
            while True:
                # Non blocking read.
                _data = self.s.read(self.s.in_waiting)
                yield from self.raw_sensor_data_queue.put(_data)
                yield from asyncio.sleep(self.read_delay)
        except SerialException as err:
            lgr.exception(err)
            self.s.close()
            self.bus.stop_test('Error reading from serial port.')
        except CancelledError:
            self.s.close()
            lgr.info("Stopped Serial sensor")

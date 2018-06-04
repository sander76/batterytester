import logging
from concurrent.futures import ThreadPoolExecutor

from serial import Serial, SerialException

from batterytester.components.sensor.connector import AsyncSensorConnector
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


class ArduinoConnector(AsyncSensorConnector):
    """Arduino based squid connector.
    Listen method is adapted to incoming squid line protocol."""

    def __init__(
            self, *,
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

    def get_version(self):
        if self.s.is_open:
            self.s.write('{i}')

    async def close_method(self):
        """Close the serial port. This gets called after the main test
        has stopped.

        Closing the serial port will raise a Serial Exception in the
        threaded serial listener effectively stopping
        the wrapping async task"""
        LOGGER.debug("Closing serial connection")
        self.s.cancel_read()
        self.s.close()

    def _connect(self):
        if not self.s.is_open:
            try:
                LOGGER.debug(
                    "Connecting to serial port {}.".format(self.serial_port))
                self.s.open()
            except SerialException as err:
                LOGGER.error(err)
                raise FatalTestFailException("Error connecting to serial port")

    def _listen_for_data(self):
        self._connect()
        while self.bus.running:
            try:
                data = self.s.readline()
                self.check_command(data)
            except SerialException:
                if self.s.is_open:
                    self.s.close()

                LOGGER.error("error reading from serial port")
                raise FatalTestFailException("Problem reading serial port.")

    def check_command(self, data):
        command = data[1]
        if command == 105:  # 'i' ascii character
            LOGGER.info("sensor identity {}".format(data))
            # report version
            pass
        elif command == 115:  # 's' ascii character
            # sensor data
            self.bus.loop.call_soon_threadsafe(
                self.raw_sensor_data_queue.put_nowait, data[3:-2])

    async def async_listen_for_data(self, *args):
        with ThreadPoolExecutor(max_workers=1) as executor:
            res = await self.bus.loop.run_in_executor(
                executor, self._listen_for_data)
            return res
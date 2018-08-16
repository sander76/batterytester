import asyncio
import logging
from asyncio import CancelledError
from concurrent.futures import ThreadPoolExecutor

from serial import SerialException, Serial

from batterytester.components.sensor.connector import AsyncSensorConnector
from batterytester.core.helpers.helpers import (
    FatalTestFailException,
    SquidConnectException,
)

LOGGER = logging.getLogger(__name__)


# todo: make listening to arduino async.


class SquidConnector(AsyncSensorConnector):
    """Non blocking serial read implementation."""

    def __init__(self, *, bus, serial_port, serial_speed, try_delay=10):
        super().__init__(bus)
        # self.s = Serial()
        self.serial_port = serial_port
        self.serial_speed = serial_speed
        self.s = None  # the serial port
        self.trydelay = try_delay
        self.shutting_down = False

    def get_version(self):
        """Send a version request."""
        if self.s.is_open:
            self.s.write(b"{i}")

    async def setup(self, test_name: str, bus):
        self._connect()
        await super().setup(test_name, bus)

    async def shutdown(self, bus):
        """Close the serial port.

        This gets called after the main test has stopped.
        Closing the serial port will raise a Serial Exception in the
        threaded serial listener effectively stopping
        the wrapping async task"""

        LOGGER.info("Closing serial connection")
        self.shutting_down = True
        if self.s:
            self.s.cancel_read()
            self._close()

    def _close(self):
        if self.s.is_open:
            try:
                self.s.close()
            except (OSError, SerialException) as err:
                LOGGER.error(err)

    def _connect(self):
        try:
            LOGGER.info(
                "Connecting to serial port {}.".format(self.serial_port)
            )
            self.s = Serial(port=self.serial_port, baudrate=self.serial_speed,
                            timeout=0)
            LOGGER.info("Connected to serial port {}".format(self.serial_port))
        except (SerialException, FileNotFoundError) as err:
            LOGGER.error(err)
            raise SquidConnectException(err)

    async def read(self):
        collecting = False
        command = bytearray()
        while 1:
            # LOGGER.debug("Start read")
            char = self.s.read()
            # LOGGER.debug("incoming: {}".format(char))
            if char == b"{":
                collecting = True
                command.extend(char)

            elif char == b"}":  # carriage return
                LOGGER.debug("Incoming command: {}".format(command))
                return command
            elif collecting:
                if char != b"":
                    command.extend(char)

            await asyncio.sleep(0.05)

    async def async_listen_for_data(self, *args):
        try:
            while self.bus.running:
                command = await self.read()
                self.raw_sensor_data_queue.put_nowait(command)

        except (SerialException, IndexError):
            self._close()
            if self.shutting_down:
                LOGGER.info("Serial connection closed.")
            else:
                LOGGER.error("error reading from serial port")
                raise SquidConnectException("Problem reading serial port.")

        except CancelledError:
            LOGGER.info("Closing serial reading task.")

        except Exception as err:
            raise FatalTestFailException("Unknown problem: {}".format(err))
        finally:
            LOGGER.info("Finished reading.")
        # try:
        #     with ThreadPoolExecutor(max_workers=1) as executor:
        #         res = await self.bus.loop.run_in_executor(
        #             executor, self._listen_for_data
        #         )
        #         return res
        # except CancelledError:
        #     LOGGER.info("Closing serial task")


class ArduinoConnector(AsyncSensorConnector):
    """Arduino based squid connector.
    Listen method is adapted to incoming squid line protocol."""

    def __init__(self, *, bus, serial_port, serial_speed, try_delay=10):
        super().__init__(bus)
        # self.s = Serial()
        self.serial_port = serial_port
        self.serial_speed = serial_speed
        self.s = None  # the serial port
        self.trydelay = try_delay
        self.shutting_down = False

    def get_version(self):
        if self.s.is_open:
            self.s.write("{i}")

    async def setup(self, test_name: str, bus):
        self._connect()
        await super().setup(test_name, bus)

    async def shutdown(self, bus):
        """Close the serial port.

        This gets called after the main test has stopped.
        Closing the serial port will raise a Serial Exception in the
        threaded serial listener effectively stopping
        the wrapping async task"""

        LOGGER.info("Closing serial connection")
        self.shutting_down = True
        self.s.cancel_read()
        self._close()

    def _close(self):
        if self.s.is_open:
            try:
                self.s.close()
            except (OSError, SerialException) as err:
                LOGGER.error(err)

    def _connect(self):
        try:
            LOGGER.debug(
                "Connecting to serial port {}.".format(self.serial_port)
            )
            self.s = Serial(port=self.serial_port, baudrate=self.serial_speed)
        except SerialException as err:
            LOGGER.error(err)
            raise FatalTestFailException(err)

    def _listen_for_data(self):
        while self.bus.running:
            try:
                data = self.s.readline()
                self.check_command(data)
            except (SerialException, IndexError):
                self._close()
                if self.shutting_down:
                    LOGGER.info("Serial connection closed.")
                    break
                else:
                    LOGGER.error("error reading from serial port")
                    raise FatalTestFailException(
                        "Problem reading serial port."
                    )
            except Exception as err:
                raise FatalTestFailException("Unknown problem: {}".format(err))

    def check_command(self, data):
        command = data[1]
        if command == 105:  # 'i' ascii character
            LOGGER.info("sensor identity {}".format(data))
            # todo: add this info to an event. Like Test info ?
            # report version
            pass
        elif command == 115:  # 's' ascii character
            # sensor data
            # todo: add a timestamp here. to be sure time is correct.
            self.bus.loop.call_soon_threadsafe(
                self.raw_sensor_data_queue.put_nowait, data[3:-2]
            )

    async def async_listen_for_data(self, *args):
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                res = await self.bus.loop.run_in_executor(
                    executor, self._listen_for_data
                )
                return res
        except CancelledError:
            LOGGER.info("Closing serial task")

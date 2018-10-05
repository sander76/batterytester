import logging
from asyncio import CancelledError
from concurrent.futures import ThreadPoolExecutor

from serial import SerialException, Serial

from batterytester.components.sensor.connector import AsyncSensorConnector
from batterytester.core.bus import BusState
from batterytester.core.helpers.helpers import (
    SquidConnectException,
    FatalTestFailException,
)

LOGGER = logging.getLogger(__name__)


class AltArduinoConnector(AsyncSensorConnector):
    """Arduino based squid connector.
    Listen method is adapted to incoming squid line protocol."""

    def __init__(self, *, bus, serial_port, serial_speed=115200, try_delay=10):
        super().__init__(bus)
        # self.s = Serial()
        self.serial_port = serial_port
        self.serial_speed = serial_speed
        self.s = None  # the serial port

        # todo: can below be removed ?
        self.trydelay = try_delay
        # self.shutting_down = False

    def get_version(self):
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

        LOGGER.info("Closing serial connection %s", self.serial_port)

        self._close()

    def _close(self):
        if self.s:
            try:
                LOGGER.debug("Calling close method on serial port")
                self.s.close()
            except (OSError, SerialException) as err:
                LOGGER.error(err)

    def _connect(self):
        try:
            LOGGER.debug(
                "Connecting to serial port {}.".format(self.serial_port)
            )
            # timeout is required as on linux serial.read(1) keeps blocking
            # even when serial port is closed.
            self.s = Serial(
                port=self.serial_port, baudrate=self.serial_speed, timeout=2
            )
        except SerialException as err:
            LOGGER.error(err)
            raise SquidConnectException(err)

    def _listen_for_data(self):
        while not self.bus._state == BusState.shutting_down:
            try:
                num = max(1, min(2048, self.s.in_waiting))
                data = self.s.read(num)
                self.bus.loop.call_soon_threadsafe(
                    self.raw_sensor_data_queue.put_nowait, data
                )

            except (SerialException, IndexError, TypeError) as err:
                LOGGER.info(err)
                self._close()

                if self.bus._state == BusState.shutting_down:
                    LOGGER.info("Serial connection closed.")
                    break
                else:
                    LOGGER.error("error reading from serial port")
                    raise FatalTestFailException(
                        "Problem reading serial port."
                    )
            except Exception as err:
                raise FatalTestFailException("Unknown problem: {}".format(err))

    async def async_listen_for_data(self, *args):
        try:
            with ThreadPoolExecutor(max_workers=1) as executor:
                res = await self.bus.loop.run_in_executor(
                    executor, self._listen_for_data
                )
                return res
        except CancelledError:
            LOGGER.info("Closing serial task")

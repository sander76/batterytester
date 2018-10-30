"""Actor for switching a relay on and off.

protocol: a:2:33

Activate pin2 for 33 seconds.
"""

from serial import Serial

from batterytester.components.actors.base_actor import BaseActor, \
    ACTOR_TYPE_RELAY_ACTOR
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import FatalTestFailException


def to_protocol(command, *args):
    return "{{{}:{}}}\n".format(command, ":".join(str(x) for x in args))


class RelayActor(BaseActor):
    """Relay actor connected to a serial port."""

    actor_type = ACTOR_TYPE_RELAY_ACTOR

    def __init__(self, *, serial_port, serial_speed=115200):
        self._port = serial_port
        self._speed = serial_speed
        self._serial = None

    async def setup(self, test_name: str, bus: Bus):
        self._serial = Serial(port=self._port, baudrate=self._speed)
        pass

    async def shutdown(self, bus: Bus):
        await super().shutdown(bus)
        if self._serial:
            self._serial.close()

    async def activate(self, *, pin: int, duration: int = 1):
        """Activate a relay.

        *Actor command*

        :param pin: Arduino pin number
        :param duration: in seconds.
        :return:
        """
        if duration > 99:
            raise FatalTestFailException(
                "Relay duration cannot be larger than 99 seconds."
            )

        pin = "{:02d}".format(pin)

        duration = "{:02d}".format(duration)
        _up = to_protocol("a", pin, duration)
        self._serial.write(_up.encode("utf-8"))

"""Actor for switching a relay on and off.

protocol: a:2:33

Activate pin2 for 33 seconds.
"""

from serial import Serial

from batterytester.core.actors.base_actor import BaseActor, \
    ACTOR_TYPE_RELAY_ACTOR
from batterytester.core.bus import Bus


def to_protocol(command, *args):
    return '{}:{}\n'.format(command, ':'.join(str(x) for x in args))


class RelayActor(BaseActor):
    actor_type = ACTOR_TYPE_RELAY_ACTOR

    def __init__(self, serial_port, serial_speed=115200):
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
        """Activate a relay

        :param pin: Arduino pin number
        :param duration: in seconds.
        :return:
        """
        _up = to_protocol('a', pin, duration)
        self._serial.write(_up.encode('utf-8'))

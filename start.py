import argparse
import asyncio
import json

import aiohttp

from arduino_connection import ArduinoConnection
from notifier import Notifier

SERIAL_SPEED = 115200

from aiohttp import web
from serial import Serial


class BatteryTest():
    def __init__(self, serial_port, shade_id, power_view_hub_ip, notifier):
        self.loop = asyncio.get_event_loop()
        self.ir = True
        self.arduino = ArduinoConnection(self.loop, serial_port, SERIAL_SPEED)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.shade_id = shade_id
        self.ip = power_view_hub_ip
        self.url = 'http://{}/api/shades/{}'.format(power_view_hub_ip, shade_id)
        self.close_data = json.dumps({'shade': {'id': shade_id, 'positions': {'posKind1': 1, 'position1': 0}}})
        self.open_data = json.dumps({'shade': {'id': shade_id, 'positions': {'posKind1': 1, 'position1': 65535}}})
        self.notifier = notifier

        self.loop.create_task(self.get_serial_data())
        self.loop.create_task(self.cycle())


    def start(self):
        pass

    @asyncio.coroutine
    def to_pv_hub(self, session, address):
        resp = yield from session.get(address)
        print(resp.status)

    @asyncio.coroutine
    def send_open(self, shade_id):
        resp = yield from self.session.put(self.url, data=self.open_data)

    @asyncio.coroutine
    def send_close(self, shade_id):
        resp = yield from self.session.put(self.url, data=self.close_data)

    @asyncio.coroutine
    def cycle(self, loop_pause, shade_id):
        while 1:
            self.send_open(shade_id)
            yield from asyncio.sleep(loop_pause)
            if self.ir == 0:
                self.notifier.notify("Ir sensor has zero value. breaking loop. stopping measurement.")
                break
            self.send_close(shade_id)
            yield from asyncio.sleep(loop_pause)

        # ir data not ok. Closing serial connection and stopping measurements.


    @asyncio.coroutine
    def get_serial_data(self, arduino_connection):
        while 1:
            _data = yield from arduino_connection.get_byte_async()
            _line = _data.split(';')
            if _line[0] == 'v':
                # data is voltage and amps.
                _voltage = float(_line[1])
                _amps = float(_line[2])
            elif _line[0] == 'i':
                # data is the ir sensor.
                _ir = int(_line[1])
                self.ir = _ir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serialport")
    args = parser.parse_args()
    SERIAL_PORT = args.serialport
    notifier = Notifier()
    battery = BatteryTest(SERIAL_PORT, 123456, "192.168.2.10", notifier)
    battery.start()

import json
import asyncio
import logging
import threading

from arduino_connection import ArduinoConnection
import aiohttp

SERIAL_SPEED = 115200
lgr = logging.getLogger(__name__)

class BatteryTest():
    def __init__(self, serial_port, shade_id, power_view_hub_ip, loop, session, influx, command_delay=60):
        self.loop = loop
        self.ir = 1
        self.arduino = ArduinoConnection(loop, serial_port, SERIAL_SPEED)
        self.session = session
        self.shade_id = shade_id
        self.ip = power_view_hub_ip
        self.url = 'http://{}/api/shades/{}'.format(power_view_hub_ip, shade_id)
        self.close_data = json.dumps({'shade': {'id': shade_id, 'positions': {'posKind1': 1, 'position1': 0}}})
        self.open_data = json.dumps({'shade': {'id': shade_id, 'positions': {'posKind1': 1, 'position1': 65535}}})
        self.command_delay = command_delay
        self.influx = influx
        self.event=threading.Event()

        self.loop.create_task(self.get_serial_data())
        self.loop.create_task(self.cycle())
        self.loop.create_task(self.cycle_sender())


    # @asyncio.coroutine
    # def to_pv_hub(self, session, address):
    #     resp = yield from session.get(address)
    #     print(resp.status)

    @asyncio.coroutine
    def send_open(self):
        lgr.debug("Sending open command to: {}".format(self.ip))
        resp = yield from self.session.put(self.url, data=self.open_data)
        assert resp.status == 200
        yield from resp.release()
        return True

    @asyncio.coroutine
    def send_close(self):
        lgr.debug("Sending close command to: {}".format(self.ip))
        resp = yield from self.session.put(self.url, data=self.close_data)
        assert resp.status == 200
        yield from resp.release()
        return True

    @asyncio.coroutine
    def cycle(self):
        try:
            while 1:
                yield from self.send_open()
                yield from asyncio.sleep(self.command_delay)
                if self.ir == 0:
                    raise UserWarning("Ir sensor has zero value. Breaking loop. Stopping measurement.")
                #yield from self.send_close()
                yield from asyncio.sleep(self.command_delay)
        except aiohttp.errors.ClientOSError:
            lgr.info("Cannot connect to powerview hub.")
        except AssertionError as e:
            lgr.info("Something is wrong with the following PowerView ip address: {}".format(self.url))
        finally:
            lgr.info("Stopping measurements.")
            self.loop.stop()
        return
        # self.loop.stop()
        # ir data not ok. Closing serial connection and stopping measurements.

    @asyncio.coroutine
    def cycle_sender(self):
        try:
            while 1:
                yield from self.influx.sender()
                yield from asyncio.sleep(4)
        except Exception as e:
            pass

    @asyncio.coroutine
    def get_serial_data(self):
        while 1:
            _data = yield from self.arduino.get_byte_async(self.event)
            _line = _data.split(b';')
            if _line[0] == b'v':
                # data is voltage and amps.
                _voltage = float(_line[1])
                _amps = float(_line[2])
                yield from self.influx.add_data(_voltage, _amps)
            elif _line[0] == b'i':
                # data is the ir sensor.
                _ir = int(_line[1])
                self.ir = _ir

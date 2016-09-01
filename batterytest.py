import json
import asyncio
import logging
import threading
from asyncio.futures import CancelledError

from arduino_connection import ArduinoConnection
import aiohttp

from incoming_parser import IncomingParser
from states import States

SERIAL_SPEED = 115200
lgr = logging.getLogger(__name__)


class BatteryTest:
    def __init__(self, serial_port, shade_id, power_view_hub_ip, loop, session, influx, command_delay=60):
        self.loop = loop
        self.state = States()
        self.state.ir = 1
        self.parser = IncomingParser(influx, self.state)
        self.arduino = ArduinoConnection(loop, serial_port, SERIAL_SPEED)
        self.session = session
        self.shade_id = shade_id
        self.ip = power_view_hub_ip
        self.url = 'http://{}/api/shades/{}'.format(power_view_hub_ip, shade_id)
        self.close_data = json.dumps({'shade': {'id': shade_id, 'positions': {'posKind1': 1, 'position1': 0}}})
        self.open_data = json.dumps({'shade': {'id': shade_id, 'positions': {'posKind1': 1, 'position1': 65535}}})
        self.command_delay = command_delay
        self.influx = influx
        self.event = threading.Event()

        self.loop.create_task(self.get_serial_data())
        self.loop.create_task(self.cycle_up_down())
        self.loop.create_task(self.cycle_sender())

    # @asyncio.coroutine
    # def to_pv_hub(self, session, address):
    #     resp = yield from session.get(address)
    #     print(resp.status)

    @asyncio.coroutine
    def _send_open(self):
        resp = yield from self.session.put(self.url, data=self.open_data)
        assert resp.status == 200
        yield from resp.release()

    @asyncio.coroutine
    def send_open(self):
        lgr.debug("Sending open command to: {}".format(self.ip))
        yield from self._send_open()
        yield from asyncio.sleep(1)
        yield from self._send_open()
        yield from self.influx.add_open()
        return True

    @asyncio.coroutine
    def _send_close(self):
        resp = yield from self.session.put(self.url, data=self.close_data)
        assert resp.status == 200
        yield from resp.release()

    @asyncio.coroutine
    def send_close(self):
        lgr.debug("Sending close command to: {}".format(self.ip))
        yield from self._send_close()
        yield from asyncio.sleep(1)
        yield from self._send_close()
        yield from self.influx.add_close()
        return True

    @asyncio.coroutine
    def cycle_up_down(self):
        try:
            while 1:
                yield from self.send_open()
                yield from asyncio.sleep(self.command_delay)
                if self.state.ir == 0:
                    raise UserWarning("Ir sensor has zero value. Breaking loop.")
                yield from self.send_close()
                yield from asyncio.sleep(self.command_delay)
        except aiohttp.errors.ClientOSError:
            lgr.info("Cannot connect to powerview hub.")
        except AssertionError as e:
            lgr.info("Something is wrong with the following PowerView ip address: {}".format(self.url))
        except UserWarning as e:
            lgr.info(e)
        # finally:
        self.loop.stop()
        return

    @asyncio.coroutine
    def cycle_sender(self):
        '''
        coroutine to check the measurement buffer and if full to send the measurements to the database.
        :return:
        '''
        while 1:
            yield from self.influx.sender()
            yield from asyncio.sleep(4)
            # except Exception as e:
            #     self.loop.stop()

    @asyncio.coroutine
    def get_serial_data(self):
        try:
            while 1:
                _data = yield from self.arduino.get_byte_async(self.event)
                self.parser.parse(_data)
                # _line = _data.split(b';')
                # if _line[0] == b'v':
                #     # data is voltage and amps.
                #     _voltage = float(_line[1])
                #     _amps = float(_line[2])
                #     yield from self.influx.add_data(_voltage, _amps)
                # elif _line[0] == b'i':
                #     # data is the ir sensor.
                #     _ir = int(_line[1])
                #     self.ir = _ir
                #     yield from self.influx.add_ir_data(_ir)
                # else:
                #     lgr.info("incoming serial data is not correct: {}".format(_data))
                #     self.loop.stop()
        except UserWarning as e:
            lgr.info(e)
            self.loop.stop()

import asyncio

import pytest
import serial

from batterytester.components.actors import ExampleActor
from batterytester.components.sensor.connector.squid_connector import \
    AltArduinoConnector
from batterytester.components.sensor.incoming_parser.squid_parser import \
    DictParser
from batterytester.components.sensor.squid_sensor import BaseSquidSensor
from batterytester.core.atom import Atom
from batterytester.core.base_test import BaseTest
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import SquidConnectException


# todo: read this: https://faradayrf.com/unit-testing-pyserial-code/


def fake_serial(*args, **kwargs):
    s = serial.serial_for_url(url="loop://", baudrate=115200)
    return s


@pytest.fixture
def test_connection(monkeypatch):
    monkeypatch.setattr(
        "batterytester.components.sensor.connector.squid_connector.Serial",
        fake_serial)
    bus = Bus()
    connection = AltArduinoConnector(bus=bus, serial_port='abc')

    yield connection
    if connection.s:
        connection.s.close()


@pytest.fixture
def fake_squid(monkeypatch):
    monkeypatch.setattr(
        "batterytester.components.sensor.connector.squid_connector.Serial",
        fake_serial)

    class FakeSquid(BaseSquidSensor):
        async def setup(self, test_name, bus):
            self._connector = AltArduinoConnector(
                bus=bus, serial_port=self.serialport,
                serial_speed=self.serialspeed
            )
            self._sensor_data_parser = DictParser(
                bus, self.sensor_data_queue, self.sensor_prefix
            )
            await super().setup(test_name, bus)

    return FakeSquid


def test_alt_arduino_connector_fail():
    bus = Bus()
    con = AltArduinoConnector(bus=bus, serial_port="fake_port")
    with pytest.raises(SquidConnectException):
        con._connect()


def test_cancel_read(test_connection):
    loop = asyncio.get_event_loop()

    async def run():
        vals = bytearray()
        await test_connection.setup("fake_test", test_connection.bus)
        await asyncio.sleep(1)
        await test_connection.shutdown(test_connection.bus)

    loop.run_until_complete(run())


# def test_gracefull_shutdown(fake_squid):
#     test = BaseTest(test_name="test", loop_count=1)
#
#
#     actor = ExampleActor()
#     test.add_actor(actor)
#
#     sensor = fake_squid(serial_port='test')
#     test.add_sensors(sensor)
#
#
#     def get_sequence(_actors):
#         _val = (
#
#             Atom(
#                 name='open shade',
#                 duration=1,
#                 command=actor.open
#             ),
#         )
#         return _val
#
#     test.get_sequence = get_sequence
#
#     test.start_test()


def test_queue(test_connection):
    loop = asyncio.get_event_loop()

    async def run():
        vals = bytearray()
        await test_connection.setup("fake_test", test_connection.bus)
        test_connection.s.write(b'{abc')

        raw = await test_connection.raw_sensor_data_queue.get()
        vals.extend(raw)

        test_connection.s.write(b'def}')
        raw = await test_connection.raw_sensor_data_queue.get()
        vals.extend(raw)
        raw = await test_connection.raw_sensor_data_queue.get()
        vals.extend(raw)
        assert bytes(vals) == b'{abcdef}'

    loop.run_until_complete(run())

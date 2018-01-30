import asyncio
import json

import aiohttp
import logging
from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.eventloop import use_asyncio_event_loop
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import VSplit, Window, BufferControl, \
    FormattedTextControl, Layout, HSplit
from prompt_toolkit.layout.widgets import Label, TextArea

from batterytester.core.helpers.constants import KEY_ATOM_NAME, KEY_TEST_NAME

use_asyncio_event_loop()

buffer1 = Buffer()

kb = KeyBindings()

LOGGER = logging.getLogger(__name__)


class Tui:
    def __init__(self):
        self.sensor_data = TextArea(text='sensor_data', focussable=False)
        self.test_data = TextArea(text='test_data', focussable=False)
        self.atom_data = TextArea(text='atom data', focussable=False)

        self.root_container = HSplit(
            [self.test_data, self.atom_data, self.sensor_data])
        self.layout = Layout(self.root_container)
        self.app = Application(layout=self.layout, full_screen=True,
                               key_bindings=kb)

    @kb.add('q')
    def exit_(self):
        get_app().set_result(None)


# root_container = VSplit([
#     HSplit([label, label2]),
#     Window(width=1, char='|'),
#     Window(content=FormattedTextControl(text='Hello world'))
# ])

# kb = KeyBindings()




class Data:
    def __init__(self):
        self._data = {}

    def to_multi_line(self):
        _out = []
        for key, val in self._data.items():
            _out.append('{:<8},{}'.format(key, val))
        return '\n'.join(_out)

    def update(self, data):
        for key, val in data.items():
            self._data[key] = val


class Incoming:
    def __init__(self, server='http://127.0.0.1:8567/ws'):
        self.loop = asyncio.get_event_loop()
        self._server = server
        self.tui = Tui()
        self.sensor_data = Data()

    async def ws_client(self):
        LOGGER.debug("Connecting to client")
        session = aiohttp.ClientSession()
        try:
            async with session.ws_connect(self._server) as ws:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        self.parse_incoming(msg.data)
                    elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                      aiohttp.WSMsgType.CLOSING,
                                      aiohttp.WSMsgType.CLOSED):
                        await ws.close()

            await asyncio.sleep(2)
        except asyncio.CancelledError:
            print("closing websocket")
            await ws.close()
        except Exception as err:
            LOGGER.exception(err)
        finally:
            if session:
                session.close()

    async def start(self):
        app = asyncio.gather(
            self.loop.create_task(self.ws_client()),
            self.tui.app.run_async()
        )
        await app

    def parse_atom(self, data):
        pass

    def parse_test(self, data):
        pass

    def parse_sensordata(self, data):
        self.sensor_data.update(data)
        self.tui.sensor_data.text = self.sensor_data.to_multi_line()

    def parse_incoming(self, data):
        data = json.loads(data)
        if data.get(KEY_ATOM_NAME):
            self.parse_atom(data)
        elif data.get(KEY_TEST_NAME):
            self.parse_test(data)
        else:
            self.parse_sensordata(data)


loop = asyncio.get_event_loop()
try:
    incoming = Incoming()
    # tui = Tui()
    loop.run_until_complete(incoming.start())
except KeyboardInterrupt:
    pass

finally:
    loop.close()

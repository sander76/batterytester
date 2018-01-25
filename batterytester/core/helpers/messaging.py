"""Websocket server for inter process communication"""

import json
import aiohttp

from aiohttp import web

ATTR_MESSAGE_BUS_ADDRESS = '127.0.0.1'
ATTR_MESSAGE_BUS_PORT = 8567


class Messaging:
    def __init__(self, loop):
        self.sensor_sockets = []
        self.report_sockets = []
        self.loop = loop
        self.app = web.Application()
        self.app.router.add_get('/ws', self.sensor_handler)
        self.handler=None
        self.server=None
        self._report=None

    @report.setter
    def report(self,value):
        pass

    async def sensor_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.sensor_sockets.append(ws)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':
                        await ws.close()
                    if msg.data == 'sensors':
                        ws.send_str('sensors')
                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await ws.close()
        finally:
            self.sensor_sockets.remove(ws)
        return ws

    def send_sensor_data(self, measurement: dict):
        _js = json.dumps(measurement)
        for _ws in self.sensor_sockets:
            _ws.send_str(_js)

    async def start(self):
        self.handler = self.app.make_handler()
        # self.server = self.loop.run_until_complete(f)

        self.server = await self.loop.create_server(
            self.handler, ATTR_MESSAGE_BUS_ADDRESS, ATTR_MESSAGE_BUS_PORT)


    async def stop_message_bus(self):
        self.server.close()
        await self.server.wait_closed()
        await self.app.shutdown()
        await self.handler.shutdown(60.0)
        await self.app.cleanup()

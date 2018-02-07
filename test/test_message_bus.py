import asyncio
import json

import aiohttp

from batterytester.core.helpers.constants import ATTR_VALUES
from batterytester.core.datahandlers.messaging import Messaging


async def send_sensor_data(messager: Messaging):
    try:
        while 1:
            await asyncio.sleep(1)
            messager.send_sensor_data({ATTR_VALUES: {'a': 1}})
    except asyncio.CancelledError:
        print("stop sending")


async def ws_client():
    session = aiohttp.ClientSession()
    try:

        async with session.ws_connect('http://127.0.0.1:8567/ws') as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    await ws.close()
                    return msg
    finally:
        session.close()


async def server_test(loop,messager):
    #messager = Messaging(loop)
    await messager.start()
    sender = loop.create_task(send_sensor_data(messager))
    res = await ws_client()

    # closing all.
    await messager.stop_message_bus()
    sender.cancel()
    return res


def test_receive():
    loop = asyncio.get_event_loop()
    messager = Messaging(loop)

    val = loop.run_until_complete(server_test(loop,messager))
    assert json.loads(val.data) == {ATTR_VALUES: {'a': 1}}

import asyncio

import aiohttp


async def ws_client():
    session = aiohttp.ClientSession()
    try:
        async with session.ws_connect('http://127.0.0.1:8567/ws') as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    print(msg.data)
                elif msg.type in (aiohttp.WSMsgType.CLOSE,
                                  aiohttp.WSMsgType.CLOSING,
                                  aiohttp.WSMsgType.CLOSED):
                    await ws.close()
    except asyncio.CancelledError:
        print("closing websocket")
        await ws.close()
    finally:
        session.close()


def read_sensors():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(ws_client())
    except KeyboardInterrupt:
        pass
    loop.close()

if __name__=='__main__':
    read_sensors()
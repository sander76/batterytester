import asyncio
import logging
from logging.handlers import RotatingFileHandler

lgr = logging.getLogger()
lgr.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

fh = RotatingFileHandler("out.log", 'a', 1000, 5)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
lgr.addHandler(fh)
from fldr.test import Test

@asyncio.coroutine
def looper():
    while 1:
        print("going")
        yield from asyncio.sleep(2)

@asyncio.coroutine
def stopper(loop):
    yield from asyncio.sleep(10)
    loop.stop()

if __name__ == "__main__":
    loop=asyncio.get_event_loop()
    loop.create_task(looper())
    loop.create_task(stopper(loop))
    loop.run_forever()
    print('stopped')

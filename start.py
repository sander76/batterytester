import argparse
import asyncio
import json

import logging.handlers

import aiohttp
from batterytest import BatteryTest
from database import DataBase

lgr = logging.getLogger()
lgr.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
mailformatter = logging.Formatter('%(asctime)s - %(message)s')

if __name__ == "__main__":

    # logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    # parser.add_argument("--serialport")
    # parser.add_argument("--influxhost")
    # parser.add_argument("--measurement")
    # parser.add_argument("--database")
    # parser.add_argument("--email")
    # parser.add_argument("--email_pass")
    # parser.add_argument("--pvhubip")
    # parser.add_argument("--blindid")
    # parser.add_argument("--cycletime", type=float)
    args = parser.parse_args()
    config = args.config
    with open(config,'r') as fl:
        _config = json.load(fl)

    SERIAL_PORT = _config["serialport"]
    influx = _config["influxhost"]
    measurement = _config["measurement"]
    database = _config["database"]
    pvhubip = _config["pvhubip"]
    blindid = _config["blindid"]
    cycletime = _config["cycletime"]
    email = _config["from_email"]
    email_pass = _config["email_pass"]
    toemail=_config["to_email"]

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    lgr.addHandler(ch)

    # fh = logging.handlers.RotatingFileHandler("out.log", 'a', 10000, 5)
    # fh.setLevel(logging.DEBUG)
    # fh.setFormatter(formatter)
    # lgr.addHandler(fh)

    mh = logging.handlers.SMTPHandler(("smtp.gmail.com", 587), email, toemail,
                                      "batterytest {}".format(measurement),
                                      (email, email_pass), secure=())
    mh.setLevel(logging.INFO)
    mh.setFormatter(mailformatter)
    lgr.addHandler(mh)

    # get the event loop.
    loop = asyncio.get_event_loop()

    # client session.
    session = aiohttp.ClientSession(loop=loop)

    # setup the influxdb database connection and parser
    influx = DataBase(influx, database, measurement, session,loop, 10)
    lgr.info("***** starting measurement {} ******".format(measurement))

    battery = BatteryTest(serial_port=SERIAL_PORT,
                          shade_id=blindid,
                          power_view_hub_ip=pvhubip,
                          loop=loop,
                          session=session,
                          influx=influx,
                          command_delay=cycletime)
    loop.run_forever()
    lgr.info("****** stopping measurement {} ******".format(measurement))
    session.close()

    pending = asyncio.Task.all_tasks()
    battery.event.set()

    for _pending in pending:
        _pending.cancel()
    try:
        loop.run_until_complete(asyncio.gather(*pending))
    except asyncio.CancelledError:
        pass
    loop.close()

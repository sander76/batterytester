import argparse
import asyncio
import json
import logging.handlers

import aiohttp

from batterytester.helpers import get_loop, TestException
from batterytester.incoming_parser import IncomingParser

SERIAL_SPEED = 115200

from batterytester.arduino_connector import ArduinoConnector
from batterytester.powerviewlongruntest import PowerViewLongRunTest
from batterytester.database import DataBase

lgr = logging.getLogger()
lgr.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
mailformatter = logging.Formatter('%(asctime)s - %(message)s')

if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--config")

    args = parser.parse_args()
    config = args.config
    with open(config, 'r') as fl:
        _config = json.load(fl)

    # Serial port for the incoming serial data
    sensor_serial_port = _config["serialport"]
    influx_host = _config["influxhost"]
    influx_measurement = _config["measurement"]
    influx_database = _config["database"]
    pv_hub_host = _config["pvhubip"]
    pv_blind_id = _config["blindid"]
    cycletime = _config["cycletime"]
    notify_from_email = _config["from_email"]
    notify_from_email_pass = _config["email_pass"]
    notify_email_recipient = _config["to_email"]

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    lgr.addHandler(ch)

    # fh = logging.handlers.RotatingFileHandler("out.log", 'a', 10000, 5)
    # fh.setLevel(logging.DEBUG)
    # fh.setFormatter(formatter)
    # lgr.addHandler(fh)

    mh = logging.handlers.SMTPHandler(
        ("smtp.gmail.com", 587), notify_from_email, notify_email_recipient,
        "batterytest {}".format(influx_measurement),
        (notify_from_email, notify_from_email_pass), secure=())
    mh.setLevel(logging.INFO)
    mh.setFormatter(mailformatter)
    lgr.addHandler(mh)
    # todo add file logger


    # The database where measurement data is stored.
    influx_database = DataBase(
        influx_host, influx_database, influx_measurement)

    # Create a sensor connector
    sensor_data_parser = IncomingParser()
    sensor_data_connector = ArduinoConnector(sensor_data_parser,
                                             sensor_serial_port,
                                             SERIAL_SPEED)

    batterytest = PowerViewLongRunTest(
        sensor_data_connector, influx_database,
        pv_blind_id, pv_hub_host)

    try:
        batterytest.bus.start_test()
    except:
        pass

    # try:
    #     #loop.run_forever()
    #     loop.run_until_complete(batterytest.start_test())
    # except TestException as e:
    #     batterytest.stop_test()
    # finally:
    #     batterytest.stop_test()
    #     lgr.info(
    #         "****** stopping measurement {} ******".format(influx_measurement))
    #     session.close()

    # pending = asyncio.Task.all_tasks()
    #
    # for _pending in pending:
    #     _pending.cancel()
    # try:
    #     loop.run_until_complete(asyncio.gather(*pending))
    # except asyncio.CancelledError:
    #     pass
    # loop.close()

"""Websocket server for inter process communication"""

import asyncio
import json
import logging.config
import os
import sys
from argparse import ArgumentParser
from pathlib import Path

import aiohttp
import async_timeout
from aiohttp import web, WSCloseCode

import batterytester.core.helpers.message_subjects as subj
from batterytester.core.helpers.constants import KEY_SUBJECT, ATTR_SENSOR_NAME
from batterytester.core.helpers.message_data import (
    to_serializable,
    Data,
    BaseProcessData,
)

ATTR_MESSAGE_BUS_ADDRESS = "0.0.0.0"
ATTR_MESSAGE_BUS_PORT = 8567

URL_CLOSE = "close"
MSG_TYPE_ATOM = "atom"  # General info about the current atom.
MSG_TYPE_TEST = "test"  # General test information.
MSG_TYPE_STOP_TEST = "stop_test"
MSG_TYPE_ALL_TESTS = "all_tests"

CACHE_TEST_DATA = "test_data"  # Cache key where to store test info.

LOGGER = logging.getLogger(__name__)

KEY_PASS = "passed"
KEY_FAIL = "failed"
ATTR_FAILED_IDS = "failed_ids"

URL_INTERFACE = "/ws"
URL_TEST = "/ws/tester"
URL_TEST_STOP = "/test_stop"
URL_TEST_START = "/test_start"
URL_ALL_TESTS = "/all_tests"

DEFAULT_CONFIG_PATH = "/home/pi/test_configs"
DEFAULT_LOGGING_PATH = "/home/pi/test_configs/logs"

SUB_SENSOR_CACHE = "sensor_cache"


def set_current_working_folder():
    pth = os.path.dirname(os.path.abspath(__file__))
    os.chdir(pth)


class Server:
    configs_blacklist = ["__init__.py"]

    def __init__(self, config_folder=None, loop_=None):
        """Test server

        :param config_folder: Full path to the configuration test files.
        :param loop_: async event loop.
        """
        self.client_sockets = []  # connected ui clients
        self.test_ws = None  # Socket connection to the actual running test.
        self.config_folder = config_folder
        self.loop = loop_ or asyncio.get_event_loop()
        self.app = web.Application(loop=self.loop)
        self.runner = None
        self.server = None
        self.test_process = None

        set_current_working_folder()
        self.test_cache = None
        self.p_data = None
        self.clear_cache()

    @property
    def test_is_running(self):
        if self.test_process is None:
            return False
        return True

    def _add_routes(self):
        # User interface(s) connects here.
        self.app.router.add_get(
            URL_INTERFACE, self.client_ws_connection_handler
        )
        # Test connects here.
        self.app.router.add_get(URL_TEST, self.test_connection_handler)

        self.app.router.add_static("/static/", path="static", name="static")
        self.app.router.add_post(URL_TEST_START, self.test_start_handler)
        self.app.router.add_post(URL_TEST_STOP, self.stop_test_handler)
        self.app.router.add_get("/get_status", self.get_status_handler)
        self.app.router.add_get("/get_tests", self.get_tests_handler)
        self.app.router.add_post("/system_update", self.system_update)
        self.app.router.add_post(
            "/system_shutdown", self.system_shutdown_handler
        )
        self.app.router.add_get("", self.dashboard_handler)
        self.app.router.add_get("/", self.dashboard_handler)

    def start_server(self):
        """Create a web server"""
        try:
            self.loop.run_until_complete(self.start())
        except Exception as err:
            LOGGER.error(err)

    def list_configs(self) -> list:
        # todo: make the glob be recursive and skip __init__ files

        configs = []

        if self.config_folder:

            p = Path(self.config_folder)
            for pth in p.glob("**/*.py"):
                if pth.name in self.configs_blacklist:
                    continue
                rel = pth.relative_to(p)
                configs.append(
                    {"name": pth.stem, "parts": rel.parts, "str": str(rel)}
                )
        return configs

    async def dashboard_handler(self, request):
        location = "/static/control.html"
        raise web.HTTPFound(location=location)

    async def get_tests_handler(self, request):
        data = {"data": self.list_configs(), KEY_SUBJECT: MSG_TYPE_ALL_TESTS}
        return web.json_response(data)

    async def system_shutdown_handler(self, request):
        os.system("sudo shutdown now -h")

    async def system_update(self, request):
        async def update_task():
            await asyncio.sleep(5)
            os.system(". ~/batterytester/scripts/update.sh")
        self.loop.create_task(update_task())
        return web.json_response({})

    async def test_start_handler(self, request):
        LOGGER.debug("Start test handler")
        data = await request.json()
        p = str(Path(self.config_folder).joinpath(data["str"]))

        if self.test_is_running:
            return web.Response(
                text="There is another test running. Stop that one first."
            )
        else:
            self.clear_cache()

            await self._start_test_process(p)
            p_started = BaseProcessData.process_started(
                data["name"], self.test_process.pid
            )
            self.p_data.update(p_started)

            await self.ws_send_to_clients(self.p_data.to_json())
        return web.Response()

    async def _start_test_process(self, p):
        """Start a process containing a new test to run."""
        # self.clear_cache()

        # self.process_data.status = STATUS_STARTING
        # self.process_data.subj = PROCESS_STARTED
        # await self.ws_send_to_clients(self.process_data.to_json())

        self.test_process = await asyncio.create_subprocess_exec(
            sys.executable,
            p,
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            loop=self.loop,
        )
        # self.process_data.status = STATUS_RUNNING
        # self.process_data.subj = PROCESS_INFO
        # self.process_data.process_id = self.test_process.pid

        self.process_task = asyncio.ensure_future(self.manage_process())

    async def manage_process(self):
        try:
            while not self.test_process.stdout.at_eof():
                line = await self.test_process.stdout.readline()

                p_message = BaseProcessData.process_message(
                    line.decode("utf-8")
                )
                self.p_data.update(p_message)
                await self.ws_send_to_clients(p_message.to_json())

            code = await self.test_process.wait()

            LOGGER.debug("exit code: {}".format(code))

            # self.process_data.return_code = int(code)

            p_finished = BaseProcessData.process_finished(int(code))
            self.p_data.update(p_finished)

            # self.process_data.status = STATUS_FINISHED
            try:
                await self.ws_send_to_clients(p_finished.to_json())
                # await self.ws_send_to_clients(self.process_data.to_json())
            except Exception as err:
                LOGGER.exception(err)

        except Exception as err:
            LOGGER.exception(err)
            await self.stop_test()
        finally:
            self.test_process = None

    async def stop_test_handler(self, request):
        await self.stop_test()
        return web.json_response({"running": False})

    async def get_status_handler(self, request):
        # self.test_cache["process_info"] = self.process_data.to_dict()
        self.test_cache["process_info"] = self.p_data.to_dict()
        LOGGER.info("test cache: %s", self.test_cache)

        return web.json_response(self.test_cache)

    async def stop_test(self):
        """Stop the running test process."""
        if self.test_is_running:
            if self.test_ws is not None:
                try:
                    with async_timeout.timeout(5):
                        await self.test_ws.send_str(
                            json.dumps({"type": MSG_TYPE_STOP_TEST})
                        )
                except asyncio.TimeoutError:
                    LOGGER.warning("Graceful shutdown failed.")

                    # todo: this code
                    await self.close_tester_connection()

                    await self.stop_test()
            else:
                LOGGER.warning("killing the process.")

                self.test_process.kill()

    async def close_tester_connection(self):
        if self.test_ws is not None:
            try:
                with async_timeout.timeout(5):
                    await self.test_ws.close()
            except asyncio.TimeoutError:
                LOGGER.warning(
                    "unable to close the tester websocket connection"
                    "gracefully"
                )
            finally:
                self.test_ws = None
        _data = self.test_cache.get(subj.TEST_WARMUP)
        if _data:
            _data["status"] = Data("tester disconnected")
            await self.ws_send_to_clients(
                json.dumps(_data, default=to_serializable)
            )

    async def test_connection_handler(self, request):
        """Handle incoming data from the running test."""
        self.test_ws = web.WebSocketResponse()
        await self.test_ws.prepare(request)
        try:
            async for msg in self.test_ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    LOGGER.debug(msg.data)
                    _data = json.loads(msg.data)
                    await self._parse_incoming_test_data(_data, msg.data)
                elif msg.type in (
                    aiohttp.WSMsgType.CLOSE,
                    aiohttp.WSMsgType.CLOSING,
                    aiohttp.WSMsgType.CLOSED,
                ):
                    await self.close_tester_connection()
        except Exception as err:
            LOGGER.error(err)
            await self.close_tester_connection()

        return self.test_ws

    async def client_ws_connection_handler(self, request):
        """Handle websocket connection to the connected user interfaces."""
        ws = web.WebSocketResponse()

        await ws.prepare(request)

        self.client_sockets.append(ws)
        LOGGER.debug(
            "Websocket clients connected: %s", len(self.client_sockets)
        )
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    LOGGER.debug("Incoming message %s", msg.data)
                else:
                    return ws
            return ws
        finally:
            LOGGER.debug("Removing websocket client.")
            if not ws.closed:
                await ws.close()

            # Currently there is a bug in aiohttp
            # making all websocket responses equal. So python just removes any
            # response from the list. Not the closed one.
            for idx, _client in enumerate(self.client_sockets):
                if _client.closed:
                    del self.client_sockets[idx]

            # if bug removed use this:
            # self.client_sockets.remove(ws)

    async def _parse_incoming_test_data(self, data, raw):
        """Interpret incoming test data."""
        LOGGER.debug("parsing incoming test data")
        await self.ws_send_to_clients(raw)

        try:
            _subj = data[KEY_SUBJECT]

        except KeyError:
            LOGGER.error("{} has no subj defined.")
        else:
            if (
                _subj == subj.TEST_FINISHED
                or _subj == subj.TEST_FATAL
                or _subj == subj.TEST_WARMUP
                or _subj == subj.TEST_RESULT
            ):

                self._update_test_cache(data, subj.TEST_WARMUP)
            elif (
                _subj == subj.ATOM_WARMUP
                or _subj == subj.ATOM_EXECUTE
                or _subj == subj.ATOM_COLLECTING
                or _subj == subj.ATOM_RESULT
                or _subj == subj.ATOM_FINISHED
            ):

                self._update_test_cache(data, subj.ATOM_WARMUP)
            elif _subj == subj.RESULT_SUMMARY:
                self._update_test_cache(data, subj.RESULT_SUMMARY)
            elif _subj == subj.SENSOR_DATA:
                self._update_sensor_data_cache(data)
            elif _subj == subj.LOOP_WARMUP:
                self._update_test_cache(data, subj.LOOP_WARMUP)

    def _update_test_cache(self, data, cache_key):
        if cache_key not in self.test_cache:
            self.test_cache[cache_key] = {}
        for key, value in data.items():
            self.test_cache[cache_key][key] = value

    def _update_sensor_data_cache(self, data):
        self.test_cache[SUB_SENSOR_CACHE][data[ATTR_SENSOR_NAME]] = data

    def clear_cache(self):
        self.test_cache = {"sensor_cache": {"subj": SUB_SENSOR_CACHE}}
        self.p_data = BaseProcessData.base_process()
        # self.process_data = ProcessData()

    async def ws_send_to_clients(self, raw):
        # todo: catch connection errors.
        for _ws in self.client_sockets:
            await _ws.send_str(raw)

    async def close_connection(self, ws):
        """Close the websocket connection."""
        try:
            await ws.close()
        except Exception as err:
            LOGGER.error(err)

    async def shutdown(self):
        for ws in self.client_sockets:
            await ws.close(
                code=WSCloseCode.GOING_AWAY, message="server shutdown"
            )

    async def start(self):
        """Initialize this data handler"""
        self._add_routes()
        self.runner = web.AppRunner(self.app)

        await self.runner.setup()
        self.server = web.TCPSite(
            self.runner,
            host=ATTR_MESSAGE_BUS_ADDRESS,
            port=ATTR_MESSAGE_BUS_PORT,
        )
        await self.server.start()

    async def stop_data_handler(self):
        await self.shutdown()
        await self.runner.cleanup()


def get_loop():
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    return loop


def load_config(config_file: str) -> dict:
    with open(config_file, "r") as fl:
        dct = json.load(fl)
    return dct


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--config_file", default="../dev_config.json")
    args = parser.parse_args()
    _config = load_config(args.config_file)

    logging.config.dictConfig(_config["server_logging"])

    loop = get_loop()

    server = Server(config_folder=_config["test_configs"], loop_=loop)
    server.start_server()
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(server.stop_data_handler())
    loop.close()

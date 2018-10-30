"""Checks for the PowerView hub version"""
import logging

from aiopvapi.helpers.aiorequest import AioRequest, PvApiConnectionError, \
    PvApiError
from aiopvapi.hub import Hub

from batterytester.components.actors.base_actor import (
    BaseActor,
    ACTOR_TYPE_POWERVIEW_VERSION_CHECKER,
)
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import NonFatalTestFailException

LOGGER = logging.getLogger(__name__)

PROCESSOR_VERSION = "version"
OLD_PROCESSOR_VERSION = "old_version"
RADIO_VERSION = "radio_version"
OLD_RADIO_VERSION = "old_radio_version"


class PowerViewVersionChecker(BaseActor):
    actor_type = ACTOR_TYPE_POWERVIEW_VERSION_CHECKER

    def __init__(self, *, hub_ip: str):
        """
        :param hub_ip: The Powerview hub ip address. like: 192.168.2.4
        """
        self.hub_ip = hub_ip
        self.request = None
        self.hub = None
        self.radio_version = None
        self.processor_version = None

    async def setup(self, test_name: str, bus: Bus):
        self.request = AioRequest(self.hub_ip, loop=bus.loop,
                                  websession=bus.session)
        self.hub = Hub(self.request)

    async def get_version(self):
        try:
            await self.hub.query_firmware()
            ver = self._check_version()

            if ver is not None:
                return ver
        except (PvApiConnectionError, PvApiError):
            raise NonFatalTestFailException(
                "Unable to connect to PowerView hub.")

    def _check_version(self):
        _resp = None
        if self.processor_version is None:
            _resp = self._make_response()
        elif (
                not self.radio_version == self.hub.radio_version
                or not self.processor_version == self.hub.main_processor_version
        ):
            _resp = self._make_response(include_old=True)

        self.processor_version = self.hub.main_processor_version
        self.radio_version = self.hub.radio_version

        return _resp

    def _make_response(self, include_old=False):
        _ver = {
            PROCESSOR_VERSION: str(self.hub.main_processor_version),
            RADIO_VERSION: str(self.hub.radio_version),
        }
        if include_old:
            _ver[OLD_PROCESSOR_VERSION] = str(self.processor_version)
            _ver[OLD_RADIO_VERSION] = str(self.radio_version)
        return _ver

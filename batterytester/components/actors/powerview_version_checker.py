"""Checks for the PowerView hub version"""
import logging

from aiopvapi.helpers.aiorequest import AioRequest, PvApiConnectionError
from aiopvapi.hub import Hub

from batterytester.components.actors.base_actor import BaseActor, \
    ACTOR_TYPE_POWERVIEW_VERSION_CHECKER
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import AtomExecuteError

LOGGER = logging.getLogger(__name__)


class PowerViewVersionChecker(BaseActor):
    actor_type = ACTOR_TYPE_POWERVIEW_VERSION_CHECKER

    def __init__(self, *, hub_ip: str):
        """
        :param hub_ip: The Powerview hub ip address. like: 192.168.2.4
        """
        self.hub_ip = hub_ip
        self.request = None
        self.hub_entry_point = None
        self.current_radio_version = None
        self.main_processor_version = None

    async def setup(self, test_name: str, bus: Bus):
        self.request = AioRequest(self.hub_ip, loop=bus.loop,
                                  websession=bus.session)
        self.hub_entry_point = Hub(self.request)

    async def get_version(self):
        try:
            await self.hub_entry_point.query_firmware()
        except PvApiConnectionError as err:
            raise AtomExecuteError(
                'Unable to connect to PowerView hub. {}'.format(err))

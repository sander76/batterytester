from aiopvapi.helpers.powerview_util import PowerViewUtil

from batterytester.core.actors.base_actor import BaseActor, \
    ACTOR_TYPE_POWER_VIEW


class PowerViewActor(PowerViewUtil, BaseActor):
    actor_type = ACTOR_TYPE_POWER_VIEW

    def __init__(self, hub_ip, bus):
        self.hub_ip=hub_ip
        super().__init__(hub_ip, bus.loop, bus.session)

    async def setup(self, test_name, bus):
        pass

    async def warmup(self):
        await self.get_scenes()
        await self.get_shades()

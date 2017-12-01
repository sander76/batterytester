import asyncio

from aiopvapi.resources.scene import Scene
from aiopvapi.resources.shade import Shade
from aiopvapi.scenes import Scenes, ATTR_SCENE_DATA
from aiopvapi.shades import Shades, ATTR_SHADE_DATA


class PowerView:
    def __init__(self, hub_ip, loop_, session):
        self.hub_ip = hub_ip,
        self.loop = loop_,
        self.session = session

    @asyncio.coroutine
    def get_scenes(self, hub_ip, loop_, session):
        self.scenes = []
        _scenes = yield from (Scenes(hub_ip, loop_, session)).get_resources()
        for _scene in _scenes[ATTR_SCENE_DATA]:
            self.scenes.append(Scene(_scene, hub_ip, loop_, session))

    @asyncio.coroutine
    def get_shades(self, hub_ip, loop_, session):
        self.shades = []
        _shade_resource = Shades(hub_ip, loop_, session)
        _shades = yield from _shade_resource.get_resources()
        for shade in _shades[ATTR_SHADE_DATA]:
            self.shades.append(Shade(shade, hub_ip, loop_, session))

    def get_shade_by_id(self, id) -> Shade:
        for _shade in self.shades:
            if _shade.id == id:
                return _shade

    def get_scene_by_id(self, id) -> Scene:
        for _scene in self.scenes:
            if _scene.id == id:
                return _scene

    @asyncio.coroutine
    def open_shade(self, shade_id):
        _shade = self.get_shade_by_id(shade_id)
        yield from _shade.open()

    @asyncio.coroutine
    def close_shade(self, shade_id):
        _shade = self.get_shade_by_id(shade_id)
        yield from _shade.close()

    @asyncio.coroutine
    def activate_scene(self, scene_id):
        _scene = self.get_scene_by_id(scene_id)
        yield from _scene.activate()
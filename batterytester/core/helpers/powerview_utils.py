from aiopvapi.helpers.aiorequest import AioRequest
from aiopvapi.resources.room import Room
from aiopvapi.resources.scene import Scene
from aiopvapi.resources.shade import BaseShade
from aiopvapi.rooms import Rooms
from aiopvapi.scene_members import SceneMembers
from aiopvapi.scenes import Scenes
from aiopvapi.shades import Shades

from batterytester.core.helpers.helpers import FatalTestFailException


class PowerView:
    def __init__(self, hub_ip, loop_, session):
        self.request = AioRequest(hub_ip, loop=loop_, websession=session)
        self._scenes_entry_point = Scenes(self.request)
        self._rooms_entry_point = Rooms(self.request)
        self._shades_entry_point = Shades(self.request)
        self._scene_members_entry_point = SceneMembers(self.request)
        self.scenes = []
        self.shades = []
        self.rooms = []

    async def get_scenes(self):
        self.scenes = await self._scenes_entry_point.get_instances()

    async def create_scene(self, scene_name, room_id):
        _raw = await self._scenes_entry_point.create_scene(
            room_id, scene_name)
        if _raw:
            result = Scene(_raw, self.request)
            return result

    async def get_shades(self):
        self.shades = await self._shades_entry_point.get_instances()

    async def get_scene(self, scene_id) -> Scene:
        await self.get_scenes()
        return self.get_scene_by_id(scene_id)

    async def get_room(self, room_id) -> Room:
        await self.get_rooms()
        return self.get_room_by_id(room_id)

    async def get_shade(self, shade_id) -> BaseShade:
        shade = await self._shades_entry_point.get_shade(shade_id)
        return shade

    async def get_rooms(self):
        self.rooms = await self._rooms_entry_point.get_instances()

    def get_shade_by_id(self, id_: int) -> BaseShade:
        for _shade in self.shades:
            if _shade.id == id_:
                return _shade
        raise FatalTestFailException("Shade with id={} not found".format(id_))

    def get_scene_by_id(self, id_: int) -> Scene:
        for _scene in self.scenes:
            if _scene.id == id_:
                return _scene
        raise FatalTestFailException("Scene with id={} not found".format(id_))

    def get_room_by_id(self, id_) -> Room:
        for _room in self.rooms:
            if _room.id == id_:
                return _room
        raise FatalTestFailException("Room with id={} not found".format(id_))

    async def open_shade(self, shade_id):
        _shade = await self.get_shade(shade_id)
        await _shade.open()

    async def close_shade(self, shade_id):
        _shade = await self.get_shade(shade_id)
        await _shade.close()

    async def activate_scene(self, scene_id):
        _scene = await self.get_scene(scene_id)
        await _scene.activate()

    async def add_shade_to_scene(self, shade_id, scene_id, position=None):
        if position:
            _position = position
        else:
            _shade = await self.get_shade(shade_id)
            _position = await _shade.get_current_position()

        _raw = await (SceneMembers(self.request)).create_scene_member(
            _position, scene_id, shade_id
        )

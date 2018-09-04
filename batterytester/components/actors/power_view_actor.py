"""PowerView actor"""

from aiopvapi.helpers.aiorequest import AioRequest, PvApiError
from aiopvapi.resources.scene import Scene
from aiopvapi.rooms import Rooms
from aiopvapi.scene_members import SceneMembers
from aiopvapi.scenes import Scenes
from aiopvapi.shades import Shades

from batterytester.components.actors.base_actor import (
    ACTOR_TYPE_POWER_VIEW,
    BaseActor,
)
from batterytester.core.helpers.helpers import (
    NonFatalTestFailException,
    FatalTestFailException,
)


def catch_exceptions(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except PvApiError as err:
            _fatal = kwargs.get("fatal")
            if _fatal is None or _fatal is True:
                raise FatalTestFailException(
                    "problem executing command: {} {}".format(
                        func.__name__, err
                    )
                )
            raise NonFatalTestFailException(err)

    return wrapper


class PowerViewActor(BaseActor):
    """Emits API commands to a PowerView HUB."""

    actor_type = ACTOR_TYPE_POWER_VIEW

    def __init__(self, *, hub_ip: str):
        """

        :param hub_ip: The Powerview hub ip address. like: 192.168.2.4
        """
        self.hub_ip = hub_ip
        self.room = None
        self.shade = None
        self.test_name = None
        self.request = None
        self._scenes_entry_point = None
        self._rooms_entry_point = None
        self._shades_entry_point = None
        self._scene_members_entry_point = None
        self.scenes = []  # A list of scene instances
        self.shades = []  # A list of shade instances
        self.rooms = []  # A list of room instances

    async def setup(self, test_name, bus):
        self.test_name = test_name
        self.request = AioRequest(
            self.hub_ip, loop=bus.loop, websession=bus.session
        )
        self._scenes_entry_point = Scenes(self.request)
        self._rooms_entry_point = Rooms(self.request)
        self._shades_entry_point = Shades(self.request)
        self._scene_members_entry_point = SceneMembers(self.request)

    @catch_exceptions
    async def get_scene(self, scene_id) -> Scene:
        """Get a scene resource instance."""
        _scene = await self._scenes_entry_point.get_instance(scene_id)
        return _scene

    @catch_exceptions
    async def get_room(self, room_id, fatal=True):
        """Get a scene resource instance."""
        self.room = await self._rooms_entry_point.get_instance(room_id)

    @catch_exceptions
    async def get_shade(self, shade_id: int):
        self.shade = await self._shades_entry_point.get_instance(shade_id)

    @catch_exceptions
    async def move_to(self, position):
        await self.shade._move(
            self.shade._create_shade_data(position_data=position)
        )

    @catch_exceptions
    async def open_shade(self):
        """Open a shade."""
        await self.shade.open()

    @catch_exceptions
    async def close_shade(self):
        """Close a shade."""
        await self.shade.close()

    @catch_exceptions
    async def jog_shade(self):
        """Jog a shade"""
        await self.shade.jog()

    @catch_exceptions
    async def activate_scene(self, scene_id: int = None, scene: Scene = None):
        """Activate a scene

        :param scene_id: Scene id.
        :param scene: A Scene instance
        :return:
        """
        if scene_id:
            scene = await self.get_scene(scene_id)

        await scene.activate()

    @catch_exceptions
    async def create_scene(self, scene_name, room_id) -> Scene:
        """Create a scene and return the scene object.

        :raises PvApiError when something is wrong with the hub.
        """

        _raw = await self._scenes_entry_point.create_scene(room_id, scene_name)
        result = Scene(_raw, self.request)
        self.scenes.append(result)
        return result

    @catch_exceptions
    async def delete_scene(self, scene_id: int = None, scene: Scene = None):
        """Delete a scene

        :param scene_id:
        :param scene: A Scene instance
        :return:
        """
        if scene_id:
            scene = await self.get_scene(scene_id)
        return await scene.delete()

    @catch_exceptions
    async def add_shade_to_scene(self, scene_id, position=None):
        """Add a shade to a scene."""
        if position is None:
            # _shade = await self.get_shade(shade_id)
            position = await self.shade.get_current_position()

        await self._scene_members_entry_point.create_scene_member(
            position, scene_id, self.shade.id
        )

    @catch_exceptions
    async def remove_shade_from_scene(self, shade_id, scene_id):
        """Remove a shade from a scene"""
        await self._scene_members_entry_point.delete_shade_from_scene(
            shade_id, scene_id
        )

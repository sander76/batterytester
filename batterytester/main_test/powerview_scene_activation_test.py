import asyncio

from aiopvapi.helpers.constants import ATTR_ID
from aiopvapi.powerview_tool import PowerViewCommands
from aiopvapi.resources.scene import Scene
from aiopvapi.scenes import Scenes, ATTR_SCENE_DATA

from batterytester.bus import Bus, TelegramBus
from batterytester.helpers.helpers import TestFailException
from batterytester.main_test import BaseTest
from batterytester.atom import Atom


class PowerViewSceneActivationLoopTest(BaseTest):
    def __init__(self, test_name,
                 loop_count, delay, scene_ids, hub_ip, test_location=None,
                 telegram_token=None, chat_id=None):
        # todo: check whether this value is used as default
        # when no delay is defined in the test atom.
        self.delay = delay
        super().__init__(test_name, loop_count,
                         sensor_data_connector=None,
                         database=None,
                         report=None,
                         test_location=test_location,
                         telegram_token=telegram_token,
                         telegram_chat_id=chat_id

                         )
        self.hub_ip = hub_ip
        self.scene_ids = scene_ids
        self._atoms = []

        self.scenes = Scenes(self.hub_ip, self.bus.loop, self.bus.session)

    @asyncio.coroutine
    def get_scenes(self):
        _scenes = []
        _scene_resources = yield from self.scenes.get_resources()
        if _scene_resources:
            for _id in self.scene_ids:
                for _scene in _scene_resources[ATTR_SCENE_DATA]:
                    if _scene[ATTR_ID] == _id:
                        new_scene = Scene(_scene, self.hub_ip, self.bus.loop,
                                          self.bus.session)
                        _scenes.append(new_scene)
        else:
            raise TestFailException("Error getting scenes")
        if len(_scenes) == 0:
            raise TestFailException("No scenes collected")
        return _scenes

    @asyncio.coroutine
    def create_atoms(self):
        _scenes = yield from self.get_scenes()

        for _scene in _scenes:
            test_atom = Atom(_scene.name, _scene.activate, None,
                             self.delay)
            self._atoms.append(test_atom)

    @asyncio.coroutine
    def test_warmup(self):
        yield from self.create_atoms()

    def get_sequence(self):
        return self._atoms

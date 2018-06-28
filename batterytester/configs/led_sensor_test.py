
import batterytester.components.actors as actor
import batterytester.components.actors.tools
from batterytester.components.actors import PowerViewActor
from batterytester.core.atom.atom import Atom

from batterytester.components.datahandlers.messaging import Messaging
from batterytester.components.sensor import LedGateSensor
from batterytester.core.base_test import BaseTest
from batterytester.core.helpers.helpers import set_test_config

set_test_config("../dev_config.json")

test = BaseTest(test_name='base test', loop_count=2)

test.add_sensors(

    LedGateSensor(serial_port='COM6', serial_speed=115200)
    # LedGateSensor(test.bus, 'dev/ttyACM0', 115200)
)

test.add_actor(
    PowerViewActor('172.22.3.23')
    # test_frame.get_powerview_actor()
)

test.add_data_handlers(
    Messaging()
    # test_frame.get_report()
)


def get_sequence(actors):
    powerview = batterytester.components.actors.tools.get_power_view_actor(actors)

    shade_id = 6705
    room_id = 45211
    scene_name = "AA1"

    _val = (
        Atom(
            name='close shade',
            command=powerview.close_shade,
            arguments={'shade_id': shade_id},
            duration=10
        ),
        # Atom(
        #     'create scene AA',
        #     command=powerview.create_scene,
        #     arguments={'scene_name': scene_name, 'room_id': room_id},
        #     duration=5,
        #     result_key='sceneAA',
        # ),
        # Atom(
        #     'Add shade to scene AA',
        #     command=powerview.add_shade_to_scene,
        #     arguments={'shade_id': shade_id,
        #                'scene_id': RefGetter('sceneAA', 'id')},
        #     duration=5
        # ),
        Atom(name='open shade',
             duration=10,
             command=powerview.open_shade,
             arguments={'shade_id': shade_id}),
        # Atom(
        #     'Activate scene AA',
        #     command=powerview.activate_scene,
        #     arguments={'scene_id': RefGetter('sceneAA', 'id')},
        #     duration=80
        # ),
        # Atom('open shade',
        #      command=powerview.open_shade,
        #      arguments={'shade_id': shade_id},
        #      duration=30
        #      ),
        # Atom(
        #     'Delete scene AA',
        #     command=powerview.delete_scene,
        #     arguments={'scene_id': RefGetter('sceneAA', 'id')},
        #     duration=5
        # )
    )
    return _val


test.get_sequence = get_sequence

test.start_test()

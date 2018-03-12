import logging

from batterytester.core.atom import RefGetter, Atom
from batterytester.main_test.powerview_loop_test import PowerViewLoopTest


class PvLoopTest(PowerViewLoopTest):
    """Simple test for creating and activating PowerView scenes."""

    def get_sequence(self):
        _val = (

            # Atom(
            #     'close shade',
            #     command=self.powerview.close_shade,
            #     arguments={'shade_id': 6705},
            #     duration=30
            # ),
            Atom(
                'create scene AA',
                command=self.powerview.create_scene,
                arguments={'scene_name': "AA1", 'room_id': 19369},
                duration=5,
                result_key='sceneAA',
            ),
            Atom(
                'Add shade to scene AA',
                command=self.powerview.add_shade_to_scene,
                arguments={'shade_id': 12334,
                           'scene_id': RefGetter('sceneAA', 'id')},
                duration=5
            ),
            Atom(
                'Activate scene AA',
                command=self.powerview.activate_scene,
                arguments={'scene_id': RefGetter('sceneAA', 'id')},
                duration=30
            ),
            Atom(
                'Delete scene AA',
                command=self.powerview.delete_scene,
                arguments={'scene_id':RefGetter('sceneAA','id')},
                duration=5
            )
        )
        return _val


test = PvLoopTest(
    test_name='ledgate_test',
    loop_count=1,
    hub_ip='172.22.3.23',
    delay=10
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    test.start_test()

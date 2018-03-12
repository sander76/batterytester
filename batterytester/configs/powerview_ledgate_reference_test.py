from batterytester.core.atom import RefGetter
from batterytester.core.atom.boolean_reference_atom import BooleanReferenceAtom
from batterytester.main_test.powerview_ledgate_reference_test import \
    PowerViewLedgateReferenceTest


class PvLedGateReferenceTest(PowerViewLedgateReferenceTest):
    """Ledgate sensor.

    When the sensor is open it will return True.
    if sensor is blocked it will return False.
    """

    def get_sequence(self):
        _val = (

            BooleanReferenceAtom(
                'close shade',
                command=self.powerview.close_shade,
                arguments={'shade_id': 6705},
                duration=30,
                reference={'7': {'v': False}, '5': {'v': True}}
            ),

            BooleanReferenceAtom(
                'create scene AA',
                command=self.powerview.create_scene,
                arguments={'scene_name': "AA", 'room_id': 19363},
                duration=10,
                result_key='sceneAA',
                reference={}
            ),
            BooleanReferenceAtom(
                name='open shade',
                command=self.powerview.open_shade,
                arguments={'shade_id': 6705},
                duration=30,
                reference={'7': {'v': True}, '5': {'v': False}}
            )
            # ,
            # BooleanReferenceAtom(
            #     'activate scene AA',
            #     command=self.powerview.activate_scene(
            #         RefGetter('sceneAA', 'id')),
            #     duration=30,
            #     reference={'7': {'v': False}, '5': {'v': True}}
            # )
        )
        return _val


test = PvLedGateReferenceTest(
    test_name='ledgate_test',
    loop_count=10,
    serial_port='COM4',
    baud_rate=115200,
    hub_ip='172.22.3.23'
)

if __name__ == "__main__":
    test.start_test()

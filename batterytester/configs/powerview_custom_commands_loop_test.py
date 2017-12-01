from batterytester.main_test.powerview_custom_commands_reference_test import \
    PowerViewCustomCommandsReferenceTest
from batterytester.test_atom import TestAtom

test = PowerViewCustomCommandsReferenceTest(
    test_name='custom test',
    loop_count=10,
    hub_ip='192.168.0.100'
)


def get_sequence(self: PowerViewCustomCommandsReferenceTest):
    #self=args[0]
    _val = (
        TestAtom(
            name='open shade',
            command=self.powerview.open_shade,
            arguments={'shade_id': 1},
            duration=30
        ),
        TestAtom(
            name='open shade',
            command=self.powerview.open_shade,
            arguments={'shade_id': 2},
            duration=30,
        ),
        TestAtom(
            name='close shade',
            command=self.powerview.close_shade,
            arguments={'shade_id': 2},
            duration=30
        ),
        TestAtom(
            name='close shade',
            command=self.powerview.close_shade,
            arguments={'shade_id': 1},
            duration=30,
        )
    )
    return _val


test.custom_sequence = get_sequence

if __name__ == "__main__":
    test.start_test()

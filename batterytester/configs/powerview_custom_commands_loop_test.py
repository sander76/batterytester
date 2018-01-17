from batterytester.main_test.powerview_custom_commands_reference_test import \
    PowerViewCustomCommandsReferenceTest
from batterytester.core.atom import Atom

test = PowerViewCustomCommandsReferenceTest(
    test_name='custom test',
    loop_count=10,
    hub_ip='192.168.0.108'
)


def get_sequence(self: PowerViewCustomCommandsReferenceTest):
    _val = (
        Atom(
            name='open shade',
            command=self.powerview.open_shade,
            arguments={'shade_id': 61865},
            duration=20
        ),
        Atom(
            name='open shade',
            command=self.powerview.open_shade,
            arguments={'shade_id': 18918},
            duration=20,
        ),
        Atom(
            name='close shade',
            command=self.powerview.close_shade,
            arguments={'shade_id': 18918},
            duration=20
        ),
        Atom(
            name='close shade',
            command=self.powerview.close_shade,
            arguments={'shade_id': 61865},
            duration=20,
        )
    )
    return _val



test.custom_sequence = get_sequence

if __name__ == "__main__":
    test.start_test()

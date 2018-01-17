from batterytester.core.atom.boolean_reference_atom import BooleanReferenceAtom
from batterytester.main_test.powerview_ledgate_reference_test import \
    PowerViewLedgateReferenceTest


test = PowerViewLedgateReferenceTest(
    test_name='ledgate_test',
    loop_count=10,
    serial_port='COM6',
    baud_rate=9600,
    hub_ip='192.168.0.1'
)


def get_sequence(self: PowerViewLedgateReferenceTest):
    _val = (
        BooleanReferenceAtom(
            name='open shade',
            command=self.powerview.open_shade,
            duration=30,
            reference={'b': False, 'a': True, 'c': True}
        ),
        BooleanReferenceAtom(
            'close shade',
            command=self.powerview.close_shade,
            duration=30,
            reference={'b': True, 'a': False, 'c': True}
        )
    )
    return _val


test.get_sequence = get_sequence

if __name__ == "__main__":
    test.start_test()

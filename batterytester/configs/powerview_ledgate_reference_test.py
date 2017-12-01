from batterytester.main_test.powerview_ledgate_reference_test import \
    PowerViewLedgateReferenceTest, PowerView
from batterytester.test_atom.boolean_reference_test_atom import \
    BooleanReferenceTestAtom

test = PowerViewLedgateReferenceTest(
    test_name='ledgate_test',
    loop_count=10,
    serial_port='sensor_port',
    baud_rate=9600,
    hub_ip='192.168.0.1'
)


def get_sequence(self: PowerViewLedgateReferenceTest):
    _val = (
        BooleanReferenceTestAtom(
            name='open shade',
            command=self.powerview.open_shade,
            duration=30,
            reference={'b': False, 'a': True, 'c': True}
        ),
        BooleanReferenceTestAtom(
            'close shade',
            command=self.powerview.close_shade,
            duration=30,
            reference={'b': True, 'a': False, 'c': True}
        )
    )
    return _val


test.get_sequence = get_sequence

if __name__=="__main__":
    test.start_test()
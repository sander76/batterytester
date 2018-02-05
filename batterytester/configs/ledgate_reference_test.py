import asyncio

import logging

from batterytester.core.atom.boolean_reference_atom import BooleanReferenceAtom
from batterytester.main_test.ledgate_reference_test import LedgateReferenceTest

test = LedgateReferenceTest(
    test_name='ledgate_test',
    loop_count=3,
    # serial_port='ttyACM0',
    serial_port='COM4',
    baud_rate=9600
)


@asyncio.coroutine
def fake(*args, **kwargs):
    print("function called")


def get_sequence(*args):
    _val = (
        BooleanReferenceAtom(
            name='open shade',
            command=fake,
            duration=30,
            reference={'4': False}
        ),
        BooleanReferenceAtom(
            'close shade',
            command=fake,
            duration=30,
            reference={'4': True}
        )
    )
    return _val


test.get_sequence = get_sequence

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test.start_test()

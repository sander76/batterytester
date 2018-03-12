import asyncio
import logging

from batterytester.core.atom.boolean_reference_atom import BooleanReferenceAtom
from batterytester.main_test.ledgate_reference_test import LedgateReferenceTest


class ConfigLedgateReferenceTest(LedgateReferenceTest):

    async def fake_command(self,*args,**kwargs):
        await asyncio.sleep(1)
        print("function called")

    def get_sequence(self):
        _val = (
            BooleanReferenceAtom(
                name='open shade',
                command=self.fake_command,
                duration=30,
                reference={'4': False}
            ),
            BooleanReferenceAtom(
                'close shade',
                command=self.fake_command,
                duration=30,
                reference={'4': True}
            )
        )
        return _val


test = ConfigLedgateReferenceTest(
    test_name='ledgate_test',
    loop_count=3,
    # serial_port='ttyACM0',
    serial_port='COM4',
    baud_rate=115200
)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    test.start_test()

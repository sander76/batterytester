from batterytester.core.bus import Bus
from batterytester.core.datahandlers.report import Report
from batterytester.core.sensor.led_gate_sensor import LedGateSensor
from batterytester.main_test import BaseReferenceTest


class LedgateReferenceTest(BaseReferenceTest):
    """Ledgate test test ;-)"""

    def __init__(self,
                 test_name: str,
                 loop_count: int,
                 serial_port: str,
                 baud_rate: int,
                 influx_host='172.22.3.21',
                 influx_database='menc',
                 telegram_token=None,
                 telegram_chat_id=None,
                 ):
        super().__init__(
            test_name,
            loop_count
        )
        # create the sensors.

        led_gate_sensor = LedGateSensor(bus, serial_port, baud_rate)

        # create data handlers.
        # _database = Influx(bus, influx_host, influx_database, test_name)
        _report = Report(test_name)



    def get_sequence(self):
        raise NotImplementedError


test = BaseReferenceTest('test',10,False)


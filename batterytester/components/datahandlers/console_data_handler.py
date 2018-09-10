from pprint import pprint

from batterytester.components.datahandlers.base_data_handler import (
    BaseDataHandler
)


class ConsoleDataHandler(BaseDataHandler):
    """Console messaging."""

    @staticmethod
    def to_console(data):
        pprint(data)

    def event_test_finished(self, testdata):
        self.to_console("TEST FINISHED")
        self.to_console(testdata.to_dict())

    def event_test_result(self, testdata):
        super().event_test_result(testdata)

    def event_test_warmup(self, testdata):
        self.to_console("TEST WARMUP")
        self.to_console(testdata.to_dict())

    def event_atom_execute(self, testdata):
        self.to_console("ACTOR EXECUTED")
        self.to_console(testdata.to_dict())

    def event_actor_response_received(self, testdata):
        self.to_console("ACTOR RESPONSE DATA")
        self.to_console(testdata.to_dict())

    def event_atom_finished(self, testdata):
        super().event_atom_finished(testdata)

    def event_atom_warmup(self, testdata):
        super().event_atom_warmup(testdata)
        self.to_console("ATOM WARMUP")
        self.to_console(testdata.to_dict())

    def event_atom_collecting(self, testdata):
        self.to_console("ATOM STATUS")
        self.to_console(testdata.to_dict())

    def event_atom_result(self, testdata):
        self.to_console("ATOM RESULT")
        self.to_console(testdata.to_dict())

    def event_result_summary(self, testdata):
        super().event_result_summary(testdata)

    def event_loop_warmup(self, testdata):
        self.to_console("LOOP WARMUP")
        self.to_console(testdata.to_dict())

    def event_loop_finished(self, testdata):
        self.to_console("LOOP FINISHED")
        self.to_console(testdata)

    def event_sensor_data(self, testdata):
        self.to_console("SENSOR DATA")
        self.to_console(testdata)

    def event_test_fatal(self, testdata):
        self.to_console("TEST FATAL")
        self.to_console(testdata.to_dict())

    async def setup(self, test_name, bus):
        self._bus = bus
        self.test_name = test_name

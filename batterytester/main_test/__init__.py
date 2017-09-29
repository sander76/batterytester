import asyncio
import logging
import os
from asyncio.futures import CancelledError

from batterytester.connector import SensorConnector
from batterytester.database import DataBase
from batterytester.helpers.helpers import TestFailException, get_current_time, \
    check_output_location
from batterytester.helpers.report import Report

lgr = logging.getLogger(__name__)

BASE_TEST_LOCATION = 'test_results'


class BaseTest:
    def __init__(
            self,
            test_name: str,
            loop_count: int,

            bus,
            # config: BaseConfig,
            sensor_data_connector: SensorConnector = None,
            database: DataBase = None,
            report: Report = None,
            add_time_stamp_to_report=True,
            test_location: str = None,
    ):
        # self._config = config
        self.bus = bus
        self.test_name = test_name
        self.sensor_data_connector = sensor_data_connector
        self.database = database
        self.bus.add_async_task(self._messager())
        self.bus.add_async_task(self.async_test())

        self.test_location = test_name
        if test_location:
            self.test_location = os.path.join(test_location,
                                              self.test_location)
        if add_time_stamp_to_report:
            self.test_location = (
                str(int(get_current_time().strftime('%Y-%m-%d_%H-%M-%S')))
                + '_'
                + self.test_location)
        if report:
            self._report = report
        else:
            self._report = Report(self.test_location)
        self._loopcount = loop_count

    def start_test(self, add_time_stamp_to_report=True):
        if check_output_location(self.test_location):
            self._report.create_summary_file()
            self.bus._start_test()

    def handle_sensor_data(self, sensor_data):
        """Sensor data can influence the main test.
        (Like stopping the test depending on sensor data)
        """
        raise NotImplemented

    def init_test_loop(self, current_loop):
        """Loads the actual test atoms and configures them according to the
        sequence they are in.
        """

        _seq = self.get_sequence()
        _stored_atom_results = {}
        for _idx, _atom in enumerate(_seq):
            _atom.prepare_test_atom(
                self.test_location,
                _idx,
                current_loop,
                self._report,
                stored_atom_results=_stored_atom_results
            )
            # if not self._learningmode:
            #     _atom.load_ref_data(self.reference_test_location, _idx)
        self._test_sequence = _seq

    @asyncio.coroutine
    def _start_test(self):
        self._report.write_intro(self.test_name)
        self.started = get_current_time()

    @asyncio.coroutine
    def get_sequence(self):
        """Gets called to retrieve a list of test atoms to be performed.

        Must return a sequence of test atoms."""
        raise NotImplemented("No sequence of atoms to test.")

    @asyncio.coroutine
    def test_warmup(self):
        """
        actions performed on the test subject before a new test
        is started. Should raise an TestFailException when an error occurs.
        """

        pass

    @asyncio.coroutine
    def loop_warmup(self):
        """
        actions performed before a new loop with a fresh sequence test
        is started. Should raise an TestFailException when an error occurs.
        """

        pass

    @asyncio.coroutine
    def _perform_test(self, current_loop, idx, atom):
        yield from atom.execute()
        # sleeping the defined duration to gather sensor
        # data which coming in as a result of the execution
        # command
        yield from asyncio.sleep(atom.duration)

    @asyncio.coroutine
    def init_test_atom(self, loop, atom):
        """Method to be performed at the start of each new test-atom"""
        atom.report_start_test(current_loop=loop)

    def _flush_report(self):
        self._report.report_timing(self.started, get_current_time())
        self._report.write_summary_to_file()

    @asyncio.coroutine
    def async_test(self):
        _current_loop = 0
        idx = 0
        # self.bus.loop.create_task(self.)
        try:
            yield from self.bus.notifier.notify(
                "*{}*: Starting the test.".format(self.test_name))
            yield from self._start_test()
            yield from self.test_warmup()

            while self.bus.running:
                for _current_loop in range(self._loopcount):
                    self.init_test_loop(_current_loop)

                    # performing actions on test subject to get into the proper
                    # starting state.
                    yield from self.loop_warmup()
                    for idx, atom in enumerate(self._test_sequence):
                        yield from self.init_test_atom(_current_loop, atom)
                        yield from self._perform_test(
                            _current_loop, idx, atom)
                    self._report.write_summary_to_file()
                self.bus.stop_test('')

        except TestFailException as e:
            self._report.final_test_result(False, e)
            yield from self.bus.notifier.notify_fail(_current_loop, idx, e)
            # self.bus.stop_test('')
        except CancelledError:
            lgr.debug("stopping loop test")
        except Exception as e:
            lgr.exception(e)
        finally:
            # write any remaining information to file.
            self._flush_report()
            yield from self.bus.notifier.notify(
                "*{}*: Stopping test".format(
                    self.test_name))
            # self.bus.stop_test('')

    @asyncio.coroutine
    def _messager(self):
        """Long running task.
        Gets data from the sensor_data_queue
        Data is passed to handle_sensor_data method for interpretation and
        interaction.

        Finally it is added to the database."""
        if self.sensor_data_connector:
            try:
                while self.bus.running:
                    sensor_data = yield from self.sensor_data_connector.sensor_data_queue.get()
                    self.handle_sensor_data(sensor_data)

                    yield from self.database.add_to_database(sensor_data)
                lgr.debug("stopping message loop.")
            except CancelledError as e:
                return

import asyncio
import os
import logging

from asyncio import CancelledError
from typing import Union, Sequence

from batterytester.core.atom import ReferenceAtom
from batterytester.core.bus import TelegramBus, Bus
from batterytester.core.helpers.helpers import get_current_time, \
    check_output_location, TestFailException
from batterytester.core.sensor import Sensor

from batterytester.core.database import DataBase

from batterytester.core.helpers.report import Report

LOGGER = logging.getLogger(__name__)


def get_bus(telegram_token=None,telegram_chat_id=None,test_name=None):
    if telegram_token and telegram_chat_id:
        return TelegramBus(telegram_token, telegram_chat_id, test_name)
    else:
        return Bus()


class BaseTest:
    def __init__(
            self,
            bus: Bus,
            test_name: str,
            loop_count: int,
            sensor: Union[Sensor, Sequence[Sensor], None] = None,
            database: DataBase = None,
            report: Report = None,
            add_time_stamp_to_report=True,
            test_location: str = None,
            telegram_token=None,
            telegram_chat_id=None):
        """

        :param test_name: The name of the test.
        :param loop_count: The amount of loops to run
        :param sensor: A Sensor or a list of sensors (iterable)
        :param database: If a database is used.
        :param report: A specific report type. Otherwise a default is created.
        :param add_time_stamp_to_report:
        :param test_location: By default test_name is used as folder withing the folder this code is run in. test_
            location re-specifies the base folder.
        :param telegram_token: for notifications.
        :param telegram_chat_id: for notifications.
        """
        self.bus=bus
        self.test_name = test_name

        if isinstance(sensor, Sensor):
            self.sensor = (sensor,)
        else:
            self.sensor = sensor
        if self.sensor:
            self.sensor_data_queue = asyncio.Queue(loop=self.bus.loop)
            for _sensor in self.sensor:
                # Add one sensor_data_queue to all sensors.
                _sensor.sensor_data_queue = self.sensor_data_queue

        self.database = database
        self.bus.add_async_task(self._messager())
        self.bus.add_async_task(self.async_test())

        self.test_location = test_name
        if test_location:
            self.test_location = os.path.join(test_location,
                                              self.test_location)
        if add_time_stamp_to_report:
            self.test_location = (
                    get_current_time().strftime('%Y-%m-%d_%H-%M-%S')
                    + '_'
                    + self.test_location)
        if report:
            self._report = report
        else:
            self._report = Report(self.test_location)
        self._loopcount = loop_count
        self._active_atom = None
        self._active_index = None
        self._active_loop = None

    def start_test(self, add_time_stamp_to_report=True):
        """Starts the actual test."""
        if check_output_location(self.test_location):
            self._report.create_summary_file()
            self.bus._start_test()

    def handle_sensor_data(self, sensor_data: dict):
        """Handle sensor data by sending it to the active atom or store
        it in a database.
        Cannot be a blocking io call. Needs to return immediately
        """
        self.bus.message_bus.send_sensor_data(sensor_data)
        #todo: check whether this is implemented correctly at other locations.
        pass

    def _loop_init(self):
        """Loads the actual test atoms and configures them according to the
        sequence they are in.
        """

        _seq = self.get_sequence()
        # todo: checkout this and see whether it can change.
        _stored_atom_results = {}
        for _idx, _atom in enumerate(_seq):
            _atom.prepare_test_atom(
                self.test_location,
                _idx,
                self._active_loop,
                self._report,
                stored_atom_results=_stored_atom_results
            )
        self._test_sequence = _seq

    @asyncio.coroutine
    def _test_init(self):
        self._report.write_intro(self.test_name)
        self.started = get_current_time()

    def get_sequence(self):
        """Gets called to retrieve a list of test atoms to be performed.

        :return: A sequence of test atoms. (list, tuple or other iterable.)
        """
        raise NotImplemented("No sequence of atoms to test.")

    @asyncio.coroutine
    def test_warmup(self):
        """
        actions performed on the test before a new test
        is started. Must raise an TestFailException when an error occurs.
        """

        pass

    @asyncio.coroutine
    def loop_warmup(self):
        """
        actions performed before a new loop with a fresh sequence test
        is started. Must raise an TestFailException when an error occurs.
        """

        pass

    @asyncio.coroutine
    def perform_test(self):
        """The test to be performed"""
        yield from self._active_atom.execute()
        # sleeping the defined duration to gather sensor
        # data which is coming in as a result of the execution
        # command
        yield from asyncio.sleep(self._active_atom.duration)

    @asyncio.coroutine
    def atom_warmup(self):
        """method to be performed before doing an atom execution."""
        pass

    def _flush_report(self):
        self._report.report_timing(self.started, get_current_time())
        self._report.write_summary_to_file()

    @asyncio.coroutine
    def async_test(self):
        _current_loop = 0
        idx = 0
        try:
            yield from self.bus.notifier.notify('Starting the test')
            yield from self._test_init()
            yield from self.test_warmup()

            while self.bus.running:
                for _current_loop in range(self._loopcount):
                    self._active_loop = _current_loop
                    self._loop_init()

                    # performing actions on test subject to get into the proper
                    # starting state.
                    yield from self.loop_warmup()
                    for idx, atom in enumerate(self._test_sequence):
                        self._active_atom = atom
                        #self._active_index = idx
                        yield from self._atom_init()
                        yield from self.atom_warmup()
                        yield from self.perform_test()
                    self._report.write_summary_to_file()
                self.bus.stop_test('')

        except TestFailException as e:
            self._report.final_test_result(False, e)
            yield from self.bus.notifier.notify_fail(_current_loop, idx, e)
            self.bus.stop_test('')
        except CancelledError:
            LOGGER.debug("stopping loop test")
        except Exception as e:
            LOGGER.exception(e)
        finally:
            # write any remaining information to file.
            self._flush_report()
            yield from self.bus.notifier.notify(
                "*{}*: Stopping test".format(
                    self.test_name))
            self.bus.stop_test('')

    @asyncio.coroutine
    def _atom_init(self):
        """Method to be performed at the start of each new test-atom"""
        self._active_atom.report_start_test(current_loop=self._active_loop)

    @asyncio.coroutine
    def _messager(self):
        """Long running task.
        Gets data from the sensor_data_queue
        Data is passed to handle_sensor_data method for interpretation and
        interaction.

        Finally it is added to the database."""
        if self.sensor_data_queue:
            try:
                while self.bus.running:
                    sensor_data = yield from self.sensor_data_queue.get()
                    yield from self.handle_sensor_data(sensor_data)
                LOGGER.debug("stopping message loop.")
            except CancelledError as e:
                return
            except Exception as err:
                LOGGER.exception(err)


class BaseReferenceTest(BaseTest):
    def __init__(self,
                 bus,
                 test_name: str,
                 loop_count: int,
                 learning_mode,
                 sensor: Union[Sensor, Sequence[Sensor], None] = None,
                 database: DataBase = None,
                 report: Report = None,
                 add_time_stamp_to_report=True,
                 test_location: str = None,
                 telegram_token=None,
                 telegram_chat_id=None):
        super().__init__(
            bus,
            test_name,
            loop_count,
            sensor=sensor,
            database=database,
            report=report,
            add_time_stamp_to_report=add_time_stamp_to_report,
            test_location=test_location,
            telegram_token=telegram_token,
            telegram_chat_id=telegram_chat_id)
        self._learning_mode = learning_mode
        self.summary = {'total_tests': 0, 'failures': []}

    @asyncio.coroutine
    def perform_test(self):
        yield from super().perform_test()
        if not self._learning_mode:
            # Actual testing mode. reference data
            # and testing data can be compared.
            self.summary['total_tests'] += 1
            _success = self._active_atom.reference_compare()
            if not _success:
                self.summary['failures'].append(
                    (self._active_loop,  self.active_atom.idx))

    @property
    def active_atom(self) -> ReferenceAtom:
        return self._active_atom

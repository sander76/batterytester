import asyncio
import os
import logging
import batterytester.core.helpers.message_subjects as subj

from asyncio import CancelledError
from collections import OrderedDict
from typing import Union, Sequence

from batterytester.core.atom import ReferenceAtom
from batterytester.core.datahandlers import BaseDataHandler
from batterytester.core.helpers.message_data import Data, FatalData, \
    TestFinished, TestData, AtomStatus, AtomResult
from batterytester.core.helpers.constants import KEY_VALUE, KEY_TEST_NAME, \
    KEY_TEST_LOOPS, KEY_ATOM_STATUS, \
    ATOM_STATUS_EXECUTED, KEY_ERROR, \
    ATOM_STATUS_EXECUTING, ATTR_RESULT, REASON, KEY_ATOM_NAME, ATTR_TIMESTAMP, \
    ATOM_STATUS_COLLECTING
from batterytester.core.bus import Bus
from batterytester.core.helpers.helpers import get_current_time, \
    get_time_string, FatalTestFailException, get_current_timestamp, \
    NonFatalTestFailException
from batterytester.core.sensor import Sensor

from batterytester.core.database import DataBase

from batterytester.core.datahandlers.report import Report

LOGGER = logging.getLogger(__name__)


class BaseTest:
    def __init__(
            self,
            bus: Bus,
            test_name: str,
            loop_count: int,
            sensor: Union[Sensor, Sequence[Sensor], None] = None,
            data_handlers: Union[
                BaseDataHandler, Sequence[BaseDataHandler], None] = None):
        """

        :param test_name: The name of the test.
        :param loop_count: The amount of loops to run
        :param sensor: A Sensor or a list of sensors (iterable)
        :param report: A specific report type. Otherwise a default is created.
        :param add_time_stamp_to_report:
        :param test_location: By default test_name is used as folder withing the folder this code is run in. test_
            location re-specifies the base folder.
        """

        self.bus = bus
        self.test_name = test_name

        if isinstance(sensor, Sensor):
            self.sensor = (sensor,)
            # todo: manage if sensor is None
        else:
            self.sensor = sensor
        if self.sensor:
            self.sensor_data_queue = asyncio.Queue(loop=self.bus.loop)
            for _sensor in self.sensor:
                # Add one sensor_data_queue to all sensors.
                _sensor.sensor_data_queue = self.sensor_data_queue
        if data_handlers:
            if isinstance(data_handlers, BaseDataHandler):
                self.bus.register_data_handler(data_handlers)
            else:
                for _handler in data_handlers:
                    self.bus.register_data_handler(_handler)

        self.bus.add_async_task(self._messager())
        self.bus.main_test_task = asyncio.ensure_future(self.async_test())

        self._loopcount = loop_count
        self._active_atom = None
        self._active_index = None
        self._active_loop = None

    @property
    def active_atom(self) -> ReferenceAtom:
        return self._active_atom

    def start_test(self):
        """Starts the actual test."""
        LOGGER.debug("Starting the test.")
        self.bus._start_test()

    def handle_sensor_data(self, sensor_data: dict):
        """Handle sensor data by sending it to the active atom or store
        it in a database.
        Cannot be a blocking io call. Needs to return immediately
        """
        self.bus.notify(subj.SENSOR_DATA, sensor_data)

    def get_sequence(self):
        """Gets called to retrieve a list of test atoms to be performed.

        :return: A sequence of test atoms. (list, tuple or other iterable.)
        """
        raise NotImplemented("No sequence of atoms to test.")

    # def _test_warmup_data(self):
    #     """Returns an ordered dict containing test data to be used
    #     for reporting and feedback"""
    #
    #     return OrderedDict({
    #         KEY_TEST_NAME: {KEY_VALUE: self.test_name},
    #         ATTR_TIMESTAMP: {KEY_VALUE: get_current_timestamp()},
    #         KEY_TEST_LOOPS: {KEY_VALUE: self._loopcount}
    #     })

    @asyncio.coroutine
    def test_warmup(self):
        """
        actions performed on the test before a new test
        is started. Must raise an TestFailException when an error occurs.
        """

        LOGGER.debug("Test warmup")
        self.bus.notify(subj.TEST_WARMUP,
                        TestData(self.test_name, self._loopcount))

    def _loop_warmup_data(self):
        return {}

    @asyncio.coroutine
    def loop_warmup(self):
        """
        actions performed before a new loop with a fresh sequence test
        is started. Must raise an TestFailException when an error occurs.
        """
        LOGGER.debug('Warming up loop.')
        self.bus.notify(subj.LOOP_WARMUP, self._loop_warmup_data())

        _seq = self.get_sequence()
        # todo: checkout this and see whether it can change.
        _stored_atom_results = {}
        for _idx, _atom in enumerate(_seq):
            _atom.prepare_test_atom(
                _idx,
                self._active_loop,
                stored_atom_results=_stored_atom_results
            )
        self._test_sequence = _seq

    # def _atom_start_data(self):
    #     return {
    #         ATTR_TIMESTAMP: {KEY_VALUE: get_current_timestamp()},
    #         KEY_ATOM_STATUS: {KEY_VALUE: ATOM_STATUS_EXECUTING}
    #     }

    def _perform_test_data(self):
        return AtomStatus(ATOM_STATUS_EXECUTING)

    @asyncio.coroutine
    def perform_test(self):
        """The test to be performed"""
        self.bus.notify(subj.ATOM_STATUS, self._perform_test_data())

        yield from self._active_atom.execute()

        self.bus.notify(
            subj.ATOM_STATUS, AtomStatus(ATOM_STATUS_COLLECTING))

        # sleeping the defined duration to gather sensor
        # data which is coming in as a result of the execution
        # command
        yield from asyncio.sleep(self._active_atom.duration)

    @asyncio.coroutine
    def async_test(self):
        # _current_loop = 0
        # idx = 0
        try:
            yield from self.test_warmup()

            for _current_loop in range(self._loopcount):
                self._active_loop = _current_loop
                # performing actions on test subject to get into the proper
                # starting state.
                yield from self.loop_warmup()
                for idx, atom in enumerate(self._test_sequence):
                    try:
                        self._active_atom = atom
                        # self.bus.notify(subj.ATOM_START,
                        #                 self._atom_start_data())

                        yield from self.atom_warmup()
                        yield from self.perform_test()
                    except NonFatalTestFailException as err:
                        self.bus.notify(subj.ATOM_RESULT,
                                        {ATTR_RESULT: {KEY_VALUE: False},
                                         REASON: {KEY_VALUE: err}})

                self.bus.notify(subj.LOOP_FINISHED, get_current_timestamp())

            # self.bus.notify(
            #     subj.TEST_FINISHED,
            #     {ATTR_TIMESTAMP: {KEY_VALUE: get_current_timestamp()}})
        except FatalTestFailException as err:
            LOGGER.debug("FATAL ERROR: {}".format(err))
            self.bus.notify(subj.TEST_FATAL, FatalData(err))
            raise
        except CancelledError:
            LOGGER.debug("stopping loop test")
        except Exception as e:
            LOGGER.exception(e)
        finally:
            self.bus.notify(subj.TEST_FINISHED, TestFinished())

    def _atom_warmup_data(self):
        return self._active_atom.get_atom_data()

    @asyncio.coroutine
    def atom_warmup(self):
        """method to be performed before doing an atom execution."""
        self.bus.notify(subj.ATOM_WARMUP, self._atom_warmup_data())

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
                    self.handle_sensor_data(sensor_data)
                LOGGER.debug("stopping message loop.")
            except CancelledError as err:
                return
            except Exception as err:
                LOGGER.exception(err)
                raise FatalTestFailException(
                    "Something wrong with the sensor queue")


class BaseReferenceTest(BaseTest):
    def __init__(self,
                 bus,
                 test_name: str,
                 loop_count: int,
                 learning_mode,
                 sensor: Union[Sensor, Sequence[Sensor], None] = None,
                 data_handlers: Union[
                     BaseDataHandler, Sequence[BaseDataHandler], None] = None):
        super().__init__(
            bus,
            test_name,
            loop_count,
            sensor=sensor,
            data_handlers=data_handlers
        )
        self._learning_mode = learning_mode

    @asyncio.coroutine
    def perform_test(self):
        LOGGER.debug("Performing test")
        yield from super().perform_test()
        if not self._learning_mode:
            # Actual testing mode. reference data
            # and testing data can be compared.
            _success = self._active_atom.reference_compare()
            _data = AtomResult(_success)
            # _data = {ATTR_RESULT: {KEY_VALUE: _success}}
            if not _success:
                _data.reason = Data("Reference testing failed.")
            self.bus.notify(subj.ATOM_RESULT, _data)

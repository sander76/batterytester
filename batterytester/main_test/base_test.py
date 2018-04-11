import asyncio
import logging
from asyncio import CancelledError

from batterytester.core.actors.base_actor import BaseActor
from batterytester.core.atom.reference_atom import ReferenceAtom
from batterytester.core.bus import Bus
from batterytester.core.datahandlers import BaseDataHandler
from batterytester.core.helpers import message_subjects as subj
from batterytester.core.helpers.constants import ATOM_STATUS_EXECUTING, \
    ATOM_STATUS_COLLECTING, ATTR_RESULT, KEY_VALUE, REASON
from batterytester.core.helpers.helpers import NonFatalTestFailException, \
    get_current_timestamp, FatalTestFailException
from batterytester.core.helpers.message_data import LoopData, AtomStatus, \
    AtomResult, Data, TestData, TestFinished
from batterytester.core.sensor import Sensor

LOGGER = logging.getLogger(__name__)


class BaseTest:
    def __init__(
            self, *,
            test_name: str,
            loop_count: int,
            learning_mode: bool = False):

        self.bus = Bus()
        self.test_name = test_name
        self.sensor_data_queue = None
        self._test_sequence = None
        self._loopcount = loop_count
        self._active_atom = None
        self._active_index = None
        self._active_loop = None
        self._learning_mode = learning_mode

    def add_sensors(self, *sensors: Sensor):
        """Add sensors to the test."""
        if not self.sensor_data_queue:
            self.sensor_data_queue = asyncio.Queue(loop=self.bus.loop)
            self.bus.add_async_task((self._messager()))
        for _sensor in sensors:
            # todo: move the sensor_data_queue to the bus.
            # todo: initialize the sensor data queue in the setup method
            _sensor.sensor_data_queue = self.sensor_data_queue

            self.bus.sensors.append(_sensor)

    def add_data_handlers(self, *args: BaseDataHandler):
        """Add data handlers to the test."""

        for _handler in args:
            self.bus.register_data_handler(_handler, self.test_name)

    def add_actor(self, *actors: BaseActor):
        """Add actors to the test."""
        for _actor in actors:
            self.bus.actors[_actor.actor_type] = _actor

    def add_sequence(self, sequence):
        self.get_sequence = sequence

    @property
    def active_atom(self) -> ReferenceAtom:
        return self._active_atom

    def start_test(self):
        """Start the actual test."""
        LOGGER.debug("Starting the test.")
        try:
            self.bus._start_test(self.async_test(), self.test_name)
        except KeyboardInterrupt:
            self.bus.test_runner_task.cancel()

    def handle_sensor_data(self, sensor_data: dict):
        """Handle sensor data by sending it to the active atom or store
        it in a database.
        Cannot be a blocking io call. Needs to return immediately
        """
        self.bus.notify(subj.SENSOR_DATA, sensor_data)

        if self.active_atom:
            self.active_atom.sensor_data.append(sensor_data)

    def get_sequence(self, *args):
        """Gets called to retrieve a list of test atoms to be performed.

        :return: A sequence of test atoms. (list, tuple or other iterable.)
        """
        raise NotImplemented("No sequence of atoms to test.")

    async def test_warmup(self):
        """
        actions performed on the test before a new test
        is started. Must raise an TestFailException when an error occurs.
        """
        for _actor in self.bus.actors.values():
            await _actor.warmup()
        LOGGER.debug("Test warmup")

    async def loop_warmup(self):
        """
        actions performed before a new loop with a fresh sequence test
        is started. Must raise an TestFailException when an error occurs.
        """
        LOGGER.debug('Warming up loop.')

        _seq = self.get_sequence(self.bus.actors)

        self.bus.notify(subj.LOOP_WARMUP,
                        LoopData([_atom.get_atom_data() for _atom in _seq]))
        # todo: checkout this and see whether it can change.
        _stored_atom_results = {}
        for _idx, _atom in enumerate(_seq):
            _atom.prepare_test_atom(
                _idx,
                self._active_loop,
                _stored_atom_results
            )
        self._test_sequence = _seq

    def _perform_test_data(self):
        return AtomStatus(ATOM_STATUS_EXECUTING)

    async def perform_test(self):
        """The test to be performed"""
        self.bus.notify(subj.ATOM_STATUS, self._perform_test_data())

        await self._active_atom.execute()

        self.bus.notify(
            subj.ATOM_STATUS, AtomStatus(ATOM_STATUS_COLLECTING))

        # sleeping the defined duration to gather sensor
        # data which is coming in as a result of the execution
        # command
        await asyncio.sleep(self._active_atom.duration)

        if not self._learning_mode and isinstance(self._active_atom,
                                                  ReferenceAtom):
            # Actual testing mode. reference data
            # and testing data can be compared.
            _success = self._active_atom.reference_compare()
            _data = AtomResult(_success)
            if not _success:
                _data.reason = Data("Reference testing failed.")
            self.bus.notify(subj.ATOM_RESULT, _data)

    async def async_test(self):
        self.bus.notify(subj.TEST_WARMUP,
                        TestData(self.test_name, self._loopcount))
        await self.test_warmup()

        for _current_loop in range(self._loopcount):
            self._active_loop = _current_loop
            # performing actions on test subject to get into the proper
            # starting state.
            await self.loop_warmup()
            for idx, atom in enumerate(self._test_sequence):
                try:
                    self._active_atom = atom
                    self.bus.notify(subj.ATOM_WARMUP,
                                    self._atom_warmup_data())
                    await self.atom_warmup()

                    await self.perform_test()
                except NonFatalTestFailException as err:
                    self.bus.notify(subj.ATOM_RESULT,
                                    {ATTR_RESULT: {KEY_VALUE: False},
                                     REASON: {KEY_VALUE: err}})

            self.bus.notify(subj.LOOP_FINISHED, get_current_timestamp())
        self.bus.notify(subj.TEST_FINISHED, TestFinished())

    def _atom_warmup_data(self):
        return self._active_atom.get_atom_data()

    async def atom_warmup(self):
        """method to be performed before doing an atom execution."""
        pass

    async def _messager(self):
        """Long running task.
        Gets data from the sensor_data_queue
        Data is passed to handle_sensor_data method for interpretation and
        interaction.

        Finally it is added to the database."""
        if self.sensor_data_queue:
            try:
                while self.bus.running:
                    sensor_data = await self.sensor_data_queue.get()
                    self.handle_sensor_data(sensor_data)
                LOGGER.debug("stopping message loop.")
            except CancelledError:
                return
            except Exception as err:
                LOGGER.exception(err)
                raise FatalTestFailException(
                    "Something wrong with the sensor queue")

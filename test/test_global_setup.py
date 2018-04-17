# scenario 1 : normal test. No reference. Sensor data incoming
from unittest.mock import MagicMock

import pytest

from batterytester.core.atom.atom import Atom
from batterytester.core.atom.reference_atom import ReferenceAtom
from test.fake_components import FakeActor, FakeBaseTest, FakeVoltsAmpsSensor, \
    FakeLedGateSensor


def get_sequence1(actors):
    fake_actor = actors[FakeActor.actor_type]  # type:FakeActor

    _seq = (
        Atom(name='open',
             command=fake_actor.open,
             duration=1
             ),
        Atom(name='close',
             command=fake_actor.close,
             arguments={'arg1': 1},
             duration=1),
    )
    return _seq


def get_sequence2(actors):
    fake_actor = actors[FakeActor.actor_type]  # type:FakeActor

    _seq = (
        Atom(name='open',
             command=fake_actor.open,
             duration=1
             ),
        Atom(name='close',
             command=fake_actor.close,
             duration=1),
        Atom(name='open',
             command=fake_actor.open,
             duration=1
             ),
    )
    return _seq


def get_sequence3(actors):
    ReferenceAtom.reference_compare = MagicMock()
    fake_actor = actors[FakeActor.actor_type]  # type:FakeActor

    _seq = (
        Atom(name='open',
             command=fake_actor.open,
             duration=1
             ),
        ReferenceAtom(
            name='close',
            command=fake_actor.close,
            duration=1, reference={})
    )
    return _seq


def get_long_sequence(actors):
    fake_actor = actors[FakeActor.actor_type]  # type:FakeActor

    _seq = (
        Atom(name='open',
             command=fake_actor.open,
             duration=30
             ),
        Atom(name='close',
             command=fake_actor.close,
             arguments={'arg1': 1},
             duration=30),
    )
    return _seq


def get_basics(loop_count=1):
    fake_test = FakeBaseTest(test_name="fake_test1", loop_count=loop_count)
    fake_test.add_sensors(FakeVoltsAmpsSensor())
    fake_test.add_actor(FakeActor())

    return fake_test


@pytest.fixture
def fake_tester_1():
    fake_test = get_basics()
    fake_test.get_sequence = get_sequence1
    return fake_test


@pytest.fixture
def fake_tester_2():
    fake_test = get_basics(loop_count=2)
    fake_test.get_sequence = get_sequence1
    return fake_test


@pytest.fixture
def fake_tester_3():
    fake_test = get_basics(loop_count=2)
    fake_test.get_sequence = get_sequence2
    return fake_test


@pytest.fixture
def fake_tester_4():
    """Provides a mix of basic and reference atoms."""
    fake_test = get_basics()
    fake_test.get_sequence = get_sequence3
    return fake_test


def test_setup1(fake_tester_1):
    fake_tester_1.start_test()
    assert len(fake_tester_1._test_sequence) == 2

    _atom0 = fake_tester_1._test_sequence[0]
    assert len(_atom0.sensor_data) > 0
    _atom1 = fake_tester_1._test_sequence[1]
    assert len(_atom1.sensor_data) > 0
    _fake_actor = fake_tester_1.bus.actors[FakeActor.actor_type]

    _fake_actor.open_mock.assert_called_once()
    _fake_actor.close_mock.assert_called_once_with(arg1=1)


def test_setup2(fake_tester_2):
    fake_tester_2.start_test()
    _fake_actor = fake_tester_2.bus.actors[FakeActor.actor_type]

    assert _fake_actor.open_mock.call_count == 2
    assert _fake_actor.close_mock.call_count == 2


def test_setup3(fake_tester_3):
    fake_tester_3.start_test()
    _fake_actor = fake_tester_3.bus.actors[FakeActor.actor_type]

    assert _fake_actor.open_mock.call_count == 4
    assert _fake_actor.close_mock.call_count == 2


def test_mix_atoms(fake_tester_4):
    fake_tester_4.start_test()
    _fake_actor = fake_tester_4.bus.actors[FakeActor.actor_type]

    assert _fake_actor.open_mock.call_count == 1
    assert _fake_actor.close_mock.call_count == 1

    _reference_atom = fake_tester_4._test_sequence[1]
    _reference_atom.reference_compare.assert_called_once()


def test_influx(fake_test: FakeBaseTest, fake_actor, fake_sensor, fake_influx):
    fake_test.add_actor(fake_actor)
    fake_test.add_sensors(fake_sensor)
    fake_test.add_data_handlers(fake_influx)
    fake_test.get_sequence = get_sequence1
    fake_test.start_test()

    fake_influx._send.mock.assert_called()

    print(len(fake_influx.data))


def test_fake_ledgate_reference(fake_test: FakeBaseTest, fake_actor):
    fake_test.add_actor(fake_actor)
    fake_test.add_sensors(FakeLedGateSensor())


# def test_stop_test(fake_test: FakeBaseTest, fake_messaging, fake_actor):
#     #todo: fails when no server is running.
#     # fake_test.add_data_handlers(fake_messaging)
#     fake_test.add_actor(fake_actor)
#     fake_test.get_sequence = get_long_sequence
#
#     fake_test.start_test()
#
#     assert True

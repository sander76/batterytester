import pytest


from batterytester.components.actors import PowerViewActor
from batterytester.components.actors.base_actor import ACTOR_TYPE_POWER_VIEW
from batterytester.core.atom.atom import Atom

from test.conftest import AsyncMock
from test.fake_components import FakeBaseTest


@pytest.fixture
def fake_powerview_actor():
    fake_pv = PowerViewActor('172.3.3.1')
    fake_pv.open_shade = AsyncMock()
    fake_pv.close_shade = AsyncMock()
    fake_pv.warmup = AsyncMock()
    return fake_pv


def get_pv_sequence(actors):
    powerview = actors[ACTOR_TYPE_POWER_VIEW]  # type: PowerViewActor
    shade_id = 123

    _val = (
        Atom(name='close',
             command=powerview.close_shade,
             arguments={'shade_id': shade_id},
             duration=1
             ),
        Atom(name='open',
             command=powerview.open_shade,
             arguments={'shade_id': shade_id},
             duration=1
             )
    )
    return _val


def test_influx(fake_test: FakeBaseTest, fake_powerview_actor):
    fake_test.add_actor(fake_powerview_actor)

    fake_test.get_sequence = get_pv_sequence
    fake_test.start_test()

    fake_powerview_actor.open_shade.mock.assert_called()
    fake_powerview_actor.close_shade.mock.assert_called()


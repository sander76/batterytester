import pytest


from batterytester.components.actors import PowerViewActor
from batterytester.components.actors.base_actor import ACTOR_TYPE_POWER_VIEW
from batterytester.core.atom.atom import Atom

from test.fake_components import FakeBaseTest, AsyncMock


@pytest.fixture
def fake_powerview_actor():
    fake_pv = PowerViewActor(hub_ip='172.3.3.1')
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





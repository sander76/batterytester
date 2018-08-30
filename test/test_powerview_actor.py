import asyncio
from unittest.mock import Mock

import pytest
from aiopvapi.helpers.aiorequest import PvApiError

from batterytester.components.actors.power_view_actor import PowerViewActor
from batterytester.core.helpers.helpers import (
    FatalTestFailException,
    NonFatalTestFailException,
)

# todo: finish this testing


async def raiser(*args, **kwargs):
    raise PvApiError("test error")


async def mocker(*args, **kwargs):
    return Mock(*args, **kwargs)


@pytest.fixture
def test_actor(monkeypatch):
    actor = PowerViewActor(hub_ip="no_ip")
    monkeypatch.setattr(
        "batterytester.components.actors.power_view_actor.Scenes", Mock
    )
    monkeypatch.setattr(
        "batterytester.components.actors.power_view_actor.Rooms", Mock
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(actor.setup("fake", Mock()))
    return actor


def test_get_room(test_actor):
    loop = asyncio.get_event_loop()
    test_actor._rooms_entry_point.get_instance = raiser

    with pytest.raises(FatalTestFailException):
        loop.run_until_complete(test_actor.get_room(123))

    with pytest.raises(NonFatalTestFailException):
        loop.run_until_complete(test_actor.get_room(123, fatal=False))


def test_get_room_1(test_actor):
    pass


# from unittest.mock import Mock
#
# import pytest
# from aiopvapi.resources.shade import BaseShade
#
# from batterytester.components.actors import PowerViewActor
# from batterytester.components.actors.base_actor import ACTOR_TYPE_POWER_VIEW
# from batterytester.core.atom.atom import Atom
# from batterytester.core.base_test import BaseTest
# from test.fake_components import AsyncMock
#
#
# @pytest.fixture
# def fake_powerview_actor():
#     fake_pv = PowerViewActor(hub_ip='172.3.3.1')
#     fake_pv.open_shade = AsyncMock()
#     fake_pv.close_shade = AsyncMock()
#     fake_pv.warmup = AsyncMock()
#     return fake_pv
#
#
# def get_pv_sequence(actors):
#     powerview = actors[ACTOR_TYPE_POWER_VIEW]  # type: PowerViewActor
#     shade_id = 123
#
#     _val = (
#         Atom(name='close',
#              command=powerview.close_shade,
#              arguments={'shade_id': shade_id},
#              duration=1
#              ),
#         Atom(name='open',
#              command=powerview.open_shade,
#              arguments={'shade_id': shade_id},
#              duration=1
#              )
#     )
#     return _val
#
#
# def test_exception_handling(monkeypatch):
#     async def mock_response(url, json):
#         mock = Mock()
#         mock.status = 421
#         return mock
#
#     async def warmup():
#         return
#
#     monkeypatch.setattr("aiopvapi.helpers.aiorequest.AioRequest.put",
#                         mock_response)
#     test = BaseTest(test_name='test', loop_count=1)
#     pv_actor = PowerViewActor(hub_ip='123')
#     pv_actor.warmup = warmup
#     pv_actor.get_shade()
#     test.add_actor(pv_actor)
#
#     test.get_sequence = get_pv_sequence
#
#     test.start_test()

"""Actors receive commands from the running test (the active Atom)
and activates any device connected to it.
Devices can be hubs, serial ports, sockets etc.
"""
from batterytester.core.actors.base_actor import ACTOR_TYPE_RELAY_ACTOR, \
    ACTOR_TYPE_POWER_VIEW
from batterytester.core.actors.power_view_actor import PowerViewActor
from batterytester.core.actors.relay_actor import RelayActor
from batterytester.core.helpers.helpers import TestSetupException


def _get_actor(actors, actor_type):
    _actor = actors.get(actor_type)
    if _actor:
        return _actor
    raise TestSetupException(
        "Actor {} not available in test".format(ACTOR_TYPE_RELAY_ACTOR))


def get_relay_actor(actors) -> RelayActor:
    """Return a relay actor from available actors.

    :raise TestSetupException when not available
    """
    return _get_actor(actors, ACTOR_TYPE_RELAY_ACTOR)


def get_power_view_actor(actors) -> PowerViewActor:
    """Return a PowerView actor from available actors.

     :raises TestSetupException when not available
    """

    return _get_actor(actors, ACTOR_TYPE_POWER_VIEW)

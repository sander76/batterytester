
from batterytester.components.actors import ExampleActor
from batterytester.components.actors import PowerViewActor
from batterytester.components.actors import RelayActor
from batterytester.components.actors.base_actor import ACTOR_TYPE_RELAY_ACTOR, \
    ACTOR_TYPE_POWER_VIEW, ACTOR_TYPE_EXAMPLE
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


def get_example_actor(actors) -> ExampleActor:
    """Return an example actor from available actors.

    :raises TestSetupException when not available
    """

    return _get_actor(actors, ACTOR_TYPE_EXAMPLE)
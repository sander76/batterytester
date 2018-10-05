from batterytester.components.actors.base_actor import ACTOR_TYPE_RELAY_ACTOR, \
    ACTOR_TYPE_POWER_VIEW, ACTOR_TYPE_EXAMPLE, \
    ACTOR_TYPE_POWERVIEW_VERSION_CHECKER
from batterytester.components.actors.example_actor import ExampleActor
from batterytester.components.actors.power_view_actor import PowerViewActor
from batterytester.components.actors.powerview_version_checker import \
    PowerViewVersionChecker
from batterytester.components.actors.relay_actor import RelayActor
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


def get_powerview_version_checker_actor(actors) -> PowerViewVersionChecker:
    """Return a PowerView version checker actor from available actors.

         :raises TestSetupException when not available
    """

    return _get_actor(actors, ACTOR_TYPE_POWERVIEW_VERSION_CHECKER)

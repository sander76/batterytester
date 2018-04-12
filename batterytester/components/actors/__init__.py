"""Actors receive commands from the running test (the active Atom)
and activates any device connected to it.
Devices can be hubs, serial ports, sockets etc.
"""

from batterytester.components.actors.example_actor import ExampleActor
from batterytester.components.actors.power_view_actor import PowerViewActor
from batterytester.components.actors.relay_actor import RelayActor
import datetime
import logging

from batterytester.core.bus import Bus
from batterytester.core.sensor import IncomingParser

_LOGGER = logging.getLogger(__name__)


class ExampleDataParser(IncomingParser):
    def __init__(self, bus: Bus):
        IncomingParser.__init__(self, bus)

    def process(self, raw_incoming) -> list:
        """
        Raw incoming is a chunk of data that can be decorated and
        forwarded to the database immediately.
        """
        return ["{} at {}".format(raw_incoming,
                                  datetime.datetime.now().isoformat())]

import datetime

import logging

from batterytester.bus import Bus
from batterytester.incoming_parser import IncomingParser

_LOGGER = logging.getLogger(__name__)


class ExampleDataParser(IncomingParser):
    def __init__(self, bus: Bus):
        IncomingParser.__init__(self, bus)

    def process(self, raw_incoming) -> list:
        """
        Raw incoming is a chunk of data that can be decorated and
        forwarded to the database immediately.
        """
        # _LOGGER.debug("processing raw incoming sensor data %s" % raw_incoming)
        return ["{} at {}".format(raw_incoming,
                                  datetime.datetime.now().isoformat())]

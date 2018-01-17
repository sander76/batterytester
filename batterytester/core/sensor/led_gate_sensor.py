from batterytester.core.sensor import Sensor
from batterytester.core.sensor.connector.async_serial_connector import \
    AsyncSerialConnector
from batterytester.core.sensor.incoming_parser.boolean_parser import \
    BooleanParser


class LedGateSensor(Sensor):
    def __init__(self, bus, serialport, serialspeed):
        connector = AsyncSerialConnector(bus, serialport, serialspeed)
        parser = BooleanParser(bus)
        super().__init__(bus, connector, parser)

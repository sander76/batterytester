from batterytester.core.sensor import Sensor
from batterytester.core.sensor.connector.async_serial_connector import \
    AsyncSerialConnector
from batterytester.core.sensor.connector.async_threaded_serial_connector import \
    ThreadedSerialSensorConnector
from batterytester.core.sensor.incoming_parser.boolean_parser import \
    BooleanParser


class LedGateSensor(Sensor):
    def __init__(self, bus, serialport, serialspeed):
        connector = ThreadedSerialSensorConnector(bus, serialport, serialspeed)
        parser = BooleanParser(bus)
        super().__init__(bus, connector, parser)

"""A sensor consists of a connection (serial/socket etc) collecting sensor
data and a Parser which interprets the data in consumable parts"""


from batterytester.components.sensor.fake_volts_amps_sensor import FakeVoltsAmpsSensor
from batterytester.components.sensor.led_gate_sensor import LedGateSensor


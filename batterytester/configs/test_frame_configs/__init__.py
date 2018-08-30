import batterytester.components.actors
import batterytester.components.datahandlers as handlers
import batterytester.components.sensor as sensors

from batterytester.core.helpers.helpers import set_test_config

POWERVIEW_HUB = "192.168.1.11"
INFLUX_HOST = "172.22.3.21"

PORT_1 = "/dev/port_1"
PORT_2 = "/dev/port_2"
PORT_3 = "/dev/port_3"
PORT_4 = "/dev/port_4"

telegram_group_id = '-189126834'
telegram_sander = '225806649'
telegram_token = '264294846:AAHaD34CapgvSCS7Obsa8wJvsaDkplqgk_4'


def config_logging():
    """Configure default logging."""
    set_test_config("/home/pi/test_configs/test_frame_configs/config.json")


def datahandler_influxdb(host=INFLUX_HOST, database='menc'):
    """InfluxDB data handler"""


    return datahandlers.influx.Influx(host=host,
                                      database=database)


def datahandler_messaging():
    """Websocket data handler"""
    return datahandlers.messaging.Messaging()


def datahandler_report():
    """Default report."""
    return datahandlers.report.Report()


def actor_powerview(hub_ip='192.168.1.11'):
    """PowerView actor."""
    batterytester.components.actors.
    return actors.power_view_actor.PowerViewActor(hub_ip=hub_ip)


def actor_powerview_version_checker(hub_ip=POWERVIEW_HUB):
    """PowerView hub version checker."""

    return actors.powerview_version_checker.PowerViewVersionChecker(
        hub_ip=hub_ip)


def actor_switching_relay(port=PORT_2):
    """Relay actor.

    By default connected to port_2
    """

    return actors.relay_actor.RelayActor(serial_port=port)


def sensor_ledgate(port=PORT_1):
    """Led gate sensor.

    By default connected to port_1
    """
    return sensors.led_gate_sensor.LedGateSensor(
        serial_port=port)


def sensor_volts_amps(port=PORT_3):
    """Volts amps sensor.

    By default connected to port_3
    """
    return sensors.volts_amps_sensor.VoltsAmpsSensor(port=port)


def datahandler_telegram():
    """Send status updates using telegram"""

    return datahandlers.telegram.Telegram(token=telegram_token,
                                          chat_id=telegram_group_id)

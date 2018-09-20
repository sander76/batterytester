"""
Incoming parser receives incoming sensor data and cleans it.
"""

import logging

from batterytester.components.sensor.incoming_parser import get_measurement
from batterytester.components.sensor.incoming_parser.squid_parser import (
    INFO_TYPE_SENSOR,
    SquidParser,
)
from batterytester.core.helpers.helpers import FatalTestFailException

LOGGER = logging.getLogger(__name__)


class VoltAmpsIrParser(SquidParser):
    """Volts amps parser"""

    sensor_name = "VI"

    def __init__(self, bus, sensor_queue, sensor_prefix=None):
        super().__init__(bus, sensor_queue, sensor_prefix=sensor_prefix)
        self.sensor_name = self.decorate_sensor_name(
            VoltAmpsIrParser.sensor_name
        )

    def finalize(self):
        """Cast parsed squid data to the correct type.

        Parses to: {volts: <value>,amps: <value>}

        Finally data is emitted in form of:

        val = get_measurement(self.sensor_name,{volts: 1,amps: 2})
        amps is in milli amps
        """

        try:
            if self.current_measurement[0] == INFO_TYPE_SENSOR:
                if not len(self.current_measurement) == 5:
                    raise FatalTestFailException(
                        "Incorrect sensor data format: {}".format(
                            self.current_measurement
                        )
                    )

                data = {
                    "volts": float(self.current_measurement[2]),
                    "amps": float(self.current_measurement[4]),
                }

                self.add_to_queue(get_measurement(self.sensor_name, data))

        except (IndexError, ValueError):
            raise FatalTestFailException(
                "incoming volts amps data is not correct: {}".format(
                    self.current_measurement
                )
            )

    def add_to_queue(self, measurement):
        self.sensor_queue.put_nowait(measurement)


class DownSampledVoltsAmpsParser(VoltAmpsIrParser):
    """Parser which compares a measurement with previous measurement
    and evaluates adding to queue depending on delta values."""

    def __init__(
        self,
        bus,
        sensor_queue,
        sensor_prefix=None,
        buffer=120,
        delta_v=0.1,
        delta_a=0.5,
    ):
        """

        :param bus:
        :param sensor_queue:
        :param sensor_prefix:
        :param buffer: after <buffer> amount of measurements have come in, measurement is added to queue. Regardless.
        :param delta_v: delta Volts
        :param delta_a: delta milli Amps
        """
        super().__init__(bus, sensor_queue, sensor_prefix)
        self.buffer = buffer
        self.delta_v = delta_v
        self.delta_a = delta_a
        self.buffer_pos = 0
        self.previous_measurement = None
        self.reference_measurement = None
        # self.previous_is_sent = False

    def add_to_queue(self, measurement):
        volt = measurement["v"]["v"]["volts"]
        amps = measurement["v"]["v"]["amps"]

        # LOGGER.debug("***incoming measurement : %f %f", volt, amps)
        # LOGGER.debug("buffer position : %s", self.buffer_pos)
        if self.previous_measurement is None or self.buffer_pos == self.buffer:
            LOGGER.debug(
                "{}  {}".format(
                    measurement,
                    "Adding measurement to queue. Start or buffer full detected.",
                )
            )

            self.sensor_queue.put_nowait(measurement)
            self.buffer_pos = 0
            self.reference_measurement = measurement
        else:
            prev_volts = self.reference_measurement["v"]["v"]["volts"]
            prev_amps = self.reference_measurement["v"]["v"]["amps"]

            abs_v = abs(round(prev_volts - volt, 1))
            abs_a = abs(round(prev_amps - amps, 1))
            # LOGGER.debug("abs_v %f   abs_a %f", abs_v, abs_a)
            if abs_v >= self.delta_v or abs_a >= self.delta_a:
                # LOGGER.debug(
                #     "delta exceeds ref difference %f %f", abs_v, abs_a
                # )
                if self.buffer_pos > 1:
                    LOGGER.debug(
                        "{}  {}".format(
                            self.previous_measurement,
                            "Adding previous measurement to queue",
                        )
                    )
                    self.sensor_queue.put_nowait(self.previous_measurement)
                LOGGER.debug(
                    "{}  {}".format(
                        measurement, "Adding current measurement to queue"
                    )
                )
                self.sensor_queue.put_nowait(measurement)
                LOGGER.debug("New reference measurement %s", measurement)
                self.reference_measurement = measurement
                self.buffer_pos = 0
            # else:
            #     pass
                # LOGGER.debug("skipping measurement")
        self.previous_measurement = measurement
        self.buffer_pos += 1



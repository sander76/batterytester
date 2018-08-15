"""Tool to manange attached squids."""

import logging
import os

import serial
from serial import SerialException

LOGGER = logging.getLogger(__name__)


# query the serial ports
# get the identities


class PortManager:
    def __init__(self, async_loop, port_folder="/dev"):
        self.port_folder = port_folder
        self.allowed_ports = ["port_1", "port_2", "port_3", "port_4"]
        self.available_ports = []
        self.reading_jobs = []
        self.loop = async_loop
        self.connections = []

    def _add_reading_job(self, serial_connection):
        task = self.loop.create_task(self.read_port(serial_connection))
        self.reading_jobs.append(task)

    async def read(self, serial_port):
        command = []
        while 1:
            char = serial_port.read()
            LOGGER.debug("incoming: {}".format(char))
            if char == 13:  # carriage return
                return command
            else:
                command.append(char)

    async def read_port(self, serial_port):
        try:
            while 1:
                command = await self.read(serial_port)
                print(command)
        except SerialException:
            LOGGER.debug("Stopping reading port {}".format(serial_port))

    def scan_ports(self):
        files = os.listdir(self.port_folder)
        for file in files:
            if file in self.allowed_ports:
                self.available_ports.append(file)

    def _connect(self):
        for _port in self.available_ports:
            ser = serial.Serial(_port, baudrate=115200)
            self.connections.append(ser)
            self._add_reading_job(ser)

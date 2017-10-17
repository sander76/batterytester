import unittest
from unittest.mock import Mock

from batterytester.incoming_parser import IncomingParser
from batterytester.incoming_parser.volt_amps_ir_parser import VoltAmpsIrParser


class TestIncomingParser(unittest.TestCase):
    def setUp(self):
        mock = Mock()
        self.parser = VoltAmpsIrParser(mock)
        self.measurement = []

    def test_extract1(self):
        self.parser.incoming_data.extend(b'abc\n')
        self.parser._extract(self.measurement)
        self.assertEqual(self.measurement, [b'abc'])
        self.assertEqual(self.parser.incoming_data, b'')

    def test_extract2(self):
        self.parser.incoming_data.extend(b'abd\naa')
        self.parser._extract(self.measurement)
        self.assertEqual(self.measurement, [b'abd'])
        self.assertEqual(self.parser.incoming_data, b'aa')

    def test_extract3(self):
        self.parser.incoming_data.extend(b'abk\naa\naaa')
        self.parser._extract(self.measurement)
        self.assertEqual(self.measurement, [b'abk', b'aa'])
        self.assertEqual(self.parser.incoming_data, b'aaa')

    def test_extract4(self):
        self.parser.incoming_data.extend(b'\n')
        self.parser._extract(self.measurement)
        self.assertEqual(self.measurement, [b''])
        self.assertEqual(self.parser.incoming_data, b'')

    def test_process1(self):
        measurement = b'v;123;456\n'
        val = self.parser.process(measurement)
        self.assertEqual(val, [{'volts': 123.0, 'amps': 456.0}])

    def test_process2(self):
        measurement = b'v;222'
        val = self.parser.process(measurement)
        self.assertEqual(val, [])

    def test_process3(self):
        measurement = b'v;222\n'
        val = self.parser.process(measurement)
        self.assertEqual(val, [])

    def test_interpret(self):
        measurement = b'v;222'
        val = self.parser._interpret(measurement)
        self.assertIsNone(val)

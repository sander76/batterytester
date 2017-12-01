import unittest
from unittest.mock import Mock

from batterytester.helpers.helpers import TestFailException
from batterytester.incoming_parser.sequence_data_parser import \
    SequenceDataParser, create_sensor_data_container


class TestInterpretMethod(unittest.TestCase):
    def setUp(self):
        bus = Mock()
        self.parser = SequenceDataParser(bus)

    def test_sequence_order(self):
        self.parser._test_sequence(3)
        self.parser._test_sequence(4)
        self.parser._test_sequence(5)
        self.parser._test_sequence(0)
        self.assertEqual(self.parser._seq,5)
        self.parser._test_sequence(1)
        with self.assertRaises(TestFailException):
            self.parser._test_sequence(3)



    def test_sequence_order1(self):
        self.parser._test_sequence(3)
        self.parser._test_sequence(4)
        self.parser._test_sequence(5)
        self.parser._test_sequence(0)
        with self.assertRaises(TestFailException):
            self.parser._test_sequence(6)

    def test_for_proper_input(self):
        _input = b'123;456'
        _result = self.parser._interpret(_input)
        _expected = create_sensor_data_container(123, 456)
        self.assertDictEqual(_result, _expected)

    def test_for_string_in_input(self):
        _input = b'1a2;235'
        _result = self.parser._interpret(_input)
        self.assertIsNone(_result)


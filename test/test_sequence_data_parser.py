import unittest

from batterytester.incoming_parser.sequence_data_parser import \
    SequenceDataParser, create_sensor_data_container


class TestInterpretMethod(unittest.TestCase):
    def setUp(self):
        self.parser = SequenceDataParser()

    def test_for_proper_input(self):
        _input = b'123;456'
        _result = self.parser._interpret(_input)
        _expected = create_sensor_data_container(123, 456)
        self.assertDictEqual(_result, _expected)

    def test_for_string_in_input(self):
        _input = b'1a2;235'
        _result = self.parser._interpret(_input)
        self.assertIsNone(_result)

# class TestExtractMethod(unittest.TestCase):
#     def setUp(self):
#         self.parser=SequenceDataParser()


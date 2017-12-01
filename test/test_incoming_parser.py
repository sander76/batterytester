# import unittest
# from unittest.mock import Mock
#
# from batterytester.incoming_parser import IncomingParser
# from batterytester.incoming_parser.volt_amps_ir_parser import VoltAmpsIrParser
#
#
# class TestIncomingParser(unittest.TestCase):
#     def setUp(self):
#         mock = Mock()
#         self.parser = VoltAmpsIrParser(mock)
#         self.measurement = []
#
#     def test_process1(self):
#         measurement = b'v;123;456\n'
#         val = self.parser.process(measurement)
#         self.assertEqual(val, [{'volts': 123.0, 'amps': 456.0}])
#
#     def test_process2(self):
#         measurement = b'v;222'
#         val = self.parser.process(measurement)
#         self.assertEqual(val, [])
#
#     def test_process3(self):
#         measurement = b'v;222\n'
#         val = self.parser.process(measurement)
#         self.assertEqual(val, [])
#
#     def test_interpret(self):
#         measurement = b'v;222'
#         val = self.parser._interpret(measurement)
#         self.assertIsNone(val)

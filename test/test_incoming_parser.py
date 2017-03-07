import unittest


from batterytester.incoming_parser import IncomingParser


class TestIncomingParser(unittest.TestCase):
    def setUp(self):
        self.parser = IncomingParser()
        self.measurement = []

    def test_extract1(self):
        self.parser.incoming_data.extend(b'abc\n')
        self.parser.extract(self.measurement)
        self.assertEqual(self.measurement, [b'abc'])
        self.assertEqual(self.parser.incoming_data, b'')

    def test_extract2(self):
        self.parser.incoming_data.extend(b'abd\naa')
        self.parser.extract(self.measurement)
        self.assertEqual(self.measurement, [b'abd'])
        self.assertEqual(self.parser.incoming_data, b'aa')

    def test_extract3(self):
        self.parser.incoming_data.extend(b'abk\naa\naaa')
        self.parser.extract(self.measurement)
        self.assertEqual(self.measurement, [b'abk', b'aa'])
        self.assertEqual(self.parser.incoming_data, b'aaa')

    def test_extract4(self):
        self.parser.incoming_data.extend(b'\n')
        self.parser.extract(self.measurement)
        self.assertEqual(self.measurement, [b''])
        self.assertEqual(self.parser.incoming_data, b'')

    def test_process1(self):
        measurement = b'v;123;456\n'
        val = tuple(self.parser.process(measurement))
        self.assertEqual(val, ({'volts': 123.0,'amps': 456.0},))

    def test_process2(self):
        measurement = b'v;222'
        self.loop.run_until_complete(self.parser.process(measurement))
        self.parser.outgoing_queue.put.assert_called_once_with(
            {'volts': 123, 'amps': 456})

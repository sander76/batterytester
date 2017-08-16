import unittest

from batterytester.incoming_parser.sequence_data_parser import \
    create_sensor_data_container
from batterytester.main_test.sequence_data.comparison import Comparison, \
    ComparissonRow
from batterytester.main_test.sequence_data.test_atom import get_movement

ref_data_1 = [{'count': -6, 'start': 81, 'duration': [81]}, {'count': 270, 'start': 82, 'duration': [82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102]}]
test_data_1 = [{'count': -6, 'start': 81, 'duration': [81]}, {'count': 270, 'start': 82, 'duration': [82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102]}]

class ComparissonTest(unittest.TestCase):
    def test_deltas_true(self):
        row = ComparissonRow(10, 10, 1, 'test',2,2)
        row.do_deltas()
        self.assertEqual(row._delta_abs, 0)
        self.assertEqual(row._delta_rel, 0)
        val = row.validate()
        self.assertTrue(val)

    def test_deltas_abs_false(self):
        row = ComparissonRow(10, 11, 1, 'test', 2, 2)
        row.do_deltas()
        self.assertEqual(row._delta_abs, 1)
        self.assertEqual(row._delta_rel, 10)
        val = row.validate()
        self.assertTrue(row._delta_abs)
        self.assertTrue(row._delta_rel)
        self.assertFalse(val)

    def test_data_1(self):
        row = ComparissonRow(ref_data_1[0]['count'],test_data_1[0]['count'],1,'test',2,2)
        row.do_deltas()
        self.assertEqual(row._delta_abs, 0)
        self.assertEqual(row._delta_rel, 0)
        val = row.validate()
        self.assertTrue(val)

    def test_full_data_1(self):
        comp = Comparison(ref_data_1, test_data_1, 2, 2)
        _result = comp.do_compare()
        print(_result)

        # def setUp(self):
        #     class TestValidateAtom(unittest.TestCase):
        #         def setUp(self):
        #             self.atom = get_test_atom()
        #
        #         def test_one(self):
        #             _delta, _delta_pass, _delta_rel, _delta_rel_pass = self.atom._validate(
        #                 10, 10)
        #             self.assertEqual(_delta, 0)
        #             self.assertEqual(_delta_rel, 0)
        #             self.assertTrue(_delta_rel_pass)
        #             self.assertTrue(_delta_pass)
        #
        #         def test_two(self):
        #             _delta, _delta_pass, _delta_rel, _delta_rel_pass = self.atom._validate(
        #                 10, 11)
        #             self.assertEqual(_delta, 1)
        #             self.assertEqual(_delta_rel, 10)
        #             self.assertFalse(_delta_rel_pass)
        #             self.assertTrue(_delta_pass)
        #
        #         def test_three(self):
        #             _delta, _delta_pass, _delta_rel, _delta_rel_pass = self.atom._validate(
        #                 10, 8)
        #             self.assertEqual(_delta, -2)
        #             self.assertEqual(_delta_rel, -20)
        #             self.assertFalse(_delta_rel_pass)
        #             self.assertTrue(_delta_pass)
        #
        #         def test_four(self):
        #             _delta, _delta_pass, _delta_rel, _delta_rel_pass = self.atom._validate(
        #                 100, 95)
        #             self.assertEqual(_delta, -5)
        #             self.assertEqual(_delta_rel, -5)
        #             self.assertTrue(_delta_rel_pass)
        #             self.assertFalse(_delta_pass)

        # class TestReferenceTest(unittest.TestCase):
        #     def setUp(self):
        #         pass
        #
        #     def test_summary_length(self):
        #         _ref_data = create_sensor_data_container(20, 10)
        #         _test_data = create_sensor_data_container(20, 10)
        #         _ref_movement = [get_movement(10,_ref_data)]
        #         self.atom._sensor_reference_summary = [get_movement(10, _ref_data)]
        #         self.atom._sensor_test_summary = [get_movement(10, _test_data)]
        #         result = self.atom.reference_compare()
        #         self.assertEqual(len(result['data']),4)

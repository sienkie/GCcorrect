#!/usr/bin/env python

import unittest, os
import numpy as np
from gc_correct import correct_counts


def create_test_data(test_dir):
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    values = np.array(
        [range(0, 600, 100) + range(100, 700, 100) + [50, 50, 50, 40, 40, 60] + range(48, 60, 2)]).reshape((4, 6))
    values = values.transpose()
    with open(os.path.join(test_dir, "test_counts.txt"), "w") as f1:
        for row in values:
            f1.write("sequence\t" + "\t".join([str(value) for value in row]) + "\n")
    open(os.path.join(test_dir, "test_counts_empty.txt"), 'w').close()


class TestCorrectCounts(unittest.TestCase):
    test_dir = os.path.join(os.path.dirname(__file__), "test_data")
    # if setUp was ever run
    ClassIsSetup = False

    def setUp(self):
        # If it was not setup yet, do it
        if not self.ClassIsSetup:
            print "Initializing testing environment"
            self.setupClass()
            self.__class__.ClassIsSetup = True
        unittest.TestCase.setUp(self)

    def setupClass(self):
        create_test_data(self.__class__.test_dir)

    def test_results(self):
        counts = range(48, 60, 2)
        median = counts[2] + (counts[3] - counts[2]) / 2.0
        calculated = np.array(
            [median * 48 / 50.0, median * 50 / 50.0, median * 52 / 50.0, median * 54 / 55.0, median * 56 / 55.0,
             median * 58 / 58.0])
        i = 0
        for corrected_value in correct_counts(os.path.join(self.__class__.test_dir, "test_counts.txt"))['updated']:
            self.assertEqual(corrected_value, calculated[i])
            i += 1

    def test_columns_and_rows(self):
        self.assertEqual(correct_counts(os.path.join(self.__class__.test_dir, "test_counts.txt")).shape[1], 6)
        self.assertEqual(correct_counts(os.path.join(self.__class__.test_dir, "test_counts_empty.txt")).shape[0], 0)

    def test_arguments(self):
        self.assertRaises(IOError, correct_counts, "wrong_file_name.txt")
        self.assertRaises(IOError, correct_counts, os.path.join(os.path.dirname(__file__), "test_data"))


if __name__ == '__main__':
    unittest.main()

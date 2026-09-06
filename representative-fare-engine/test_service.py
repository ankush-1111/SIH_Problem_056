import unittest
import statistics
from service import calculate_median

class TestFareEngine(unittest.TestCase):

    def test_median_odd(self):
        fares = [5200, 5400, 5500, 5800, 7800]
        self.assertEqual(calculate_median(fares), 5500)

    def test_median_even(self):
        fares = [5200, 5400, 5500, 5800]
        self.assertEqual(calculate_median(fares), 5450)

    def test_empty(self):
        self.assertIsNone(calculate_median([]))

if __name__ == '__main__':
    unittest.main()

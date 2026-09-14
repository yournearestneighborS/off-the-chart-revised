import unittest

import pandas as pd

from offthechart.analysis import bootstrap_difference, bootstrap_mean_ci, weighted_mean


class AnalysisTests(unittest.TestCase):
    def test_weighted_mean(self):
        self.assertAlmostEqual(weighted_mean(pd.Series([1.0, 3.0]), pd.Series([1, 3])), 2.5)

    def test_bootstrap_interval_contains_mean_for_constant_sample(self):
        low, high = bootstrap_mean_ci(pd.Series([2.0, 2.0, 2.0]))
        self.assertEqual((low, high), (2.0, 2.0))

    def test_bootstrap_difference_direction(self):
        difference, low, high = bootstrap_difference(pd.Series([2, 3, 4]), pd.Series([0, 1, 2]))
        self.assertGreater(difference, 0)
        self.assertGreater(high, low)


if __name__ == "__main__":
    unittest.main()

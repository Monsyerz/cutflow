import unittest

from app.models import Cut
from app.optimizer import (
    calculate_utilization,
    calculate_waste,
    expand_cuts,
    merge_sort,
    optimize_cuts
)

class TestOptimizer(unittest.TestCase):
    def test_calculate_waste(self):
        stocks = [
            [15.0, 5.0],
            [15.0, 5.0],
            [10.5, 7.0],
            [10.5],
            [10.5]
        ]

        stock_length = 20.0
        result = calculate_waste(stocks, stock_length)
        self.assertAlmostEqual(result, 21.5, places=2)
    def test_calculate_utilization(self):

        stocks = [
            [15.0, 5.0],
            [15.0, 5.0],
            [10.5, 7.0],
            [10.5],
            [10.5]
        ]

        stock_length = 20.0
        result= calculate_utilization(stocks, stock_length)
        self.assertAlmostEqual(result, 78.5, places=2)
    def test_expand_cuts(self):
        cuts = [
            Cut(5.0, 2),
            Cut(7.0, 1),
            Cut(10.0, 3)
        ]
        expanded_cuts = expand_cuts(cuts)
        self.assertEqual(len(expanded_cuts), 6)
        self.assertEqual(expanded_cuts,[5.0, 5.0, 7.0, 10.0, 10.0, 10.0])
    def test_merge_sort(self):
        cuts = [5.0, 15.0, 7.0, 10.5, 3.0, 20.0]
        sorted_cuts = merge_sort(cuts)
        self.assertEqual(sorted_cuts, [20.0, 15.0, 10.5, 7.0, 5.0, 3.0])
    def test_optimize_cuts(self):
        cuts = [15,10,7,5]
        stock_length = 20
        result = optimize_cuts(cuts, stock_length)
        self.assertEqual(result, [[15, 5], [10, 7]])

    def test_optimize_cuts_with_large_stock_length(self):
        cuts = [15, 10, 7, 5]
        stock_length = 30
        result = optimize_cuts(cuts, stock_length)
        self.assertEqual(result, [[15, 10,5], [7]])

    def test_empty_inputs(self):
        self.assertEqual(expand_cuts([]), [])
        self.assertEqual(merge_sort([]), [])
        self.assertEqual(optimize_cuts([], 20), [])
        self.assertEqual(calculate_waste([], 20), 0)
        self.assertEqual(calculate_utilization([], 20), 0)

    def test_merge_sort_edge_cases(self):
        cases = [
            ([10], [10]),
            ([5, 10, 5, 10], [10, 10, 5, 5]),
            ([3, 7, 15], [15, 7, 3]),
            ([15, 7, 3], [15, 7, 3])
        ]

        for cuts, expected in cases:
            with self.subTest(cuts=cuts):
                self.assertEqual(merge_sort(cuts), expected)

    def test_exact_stock_fill(self):
        stocks = optimize_cuts([15, 10, 10, 5], 20)

        self.assertEqual(stocks, [[15, 5], [10, 10]])
        self.assertAlmostEqual(calculate_waste(stocks, 20), 0)
        self.assertAlmostEqual(
            calculate_utilization(stocks, 20), 100
        )

    def test_each_cut_requires_separate_stock(self):
        stocks = optimize_cuts([15, 14, 13], 20)

        self.assertEqual(stocks, [[15], [14], [13]])
        self.assertAlmostEqual(calculate_waste(stocks, 20), 18)
        self.assertAlmostEqual(
            calculate_utilization(stocks, 20), 70
        )

    def test_decimal_cut_lengths(self):
        stocks = optimize_cuts([7.5, 5.0, 2.5], 10)

        self.assertEqual(stocks, [[7.5, 2.5], [5.0]])
        self.assertAlmostEqual(calculate_waste(stocks, 10), 5)
        self.assertAlmostEqual(
            calculate_utilization(stocks, 10), 75
        )

    def test_optimizer_preserves_cuts_and_stock_capacity(self):
        cuts = [9, 8, 7, 6, 5, 4, 3, 2, 1]
        original_cuts = cuts.copy()

        stocks = optimize_cuts(cuts, 15)
        allocated_cuts = [
            cut
            for stock in stocks
            for cut in stock
        ]

        self.assertCountEqual(allocated_cuts, original_cuts)
        self.assertEqual(cuts, original_cuts)

        for stock in stocks:
            self.assertLessEqual(sum(stock), 15)

        expected_waste = len(stocks) * 15 - sum(original_cuts)
        self.assertAlmostEqual(
            calculate_waste(stocks, 15),
            expected_waste
        )

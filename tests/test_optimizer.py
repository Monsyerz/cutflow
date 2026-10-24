import unittest
from app.optimizer import calculate_utilization, calculate_waste
from app.models import Cut
from app.optimizer import expand_cuts

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
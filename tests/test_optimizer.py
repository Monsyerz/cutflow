
import unittest
from app.optimizer import calculate_utilization, calculate_waste

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

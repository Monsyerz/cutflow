import unittest
from app import create_app

class TestAPI(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })

        self.client = self.app.test_client()
    def test_api_optimize_success(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts": [
                    {"length": 15, "quantity": 2},
                    {"length": 5, "quantity": 2}
                ]
            }
        )
        self.assertEqual(response.status_code, 200)
        result = response.get_json()
        self.assertEqual(result["stocks_used"], 2)
        self.assertEqual(result["waste"], 0)
        self.assertEqual(result["total_cuts"], 4)
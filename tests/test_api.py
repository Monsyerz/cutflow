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


    def test_api_zero_stock_length(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 0,
                "cuts": [{"length": 5, "quantity": 2}]
            }
        )
        self.assertEqual(response.status_code, 400)

    def test_api_invalid_stock_length_string(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": "abc",
                "cuts": [
                    {"length": 5, "quantity": 1}
                ]
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Invalid stock length"
        )

    def test_api_empty_cuts(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts": []
            }
        )

        self.assertEqual(response.status_code, 400)


    def test_api_negative_cut_length(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts": [
                    {"length": -5, "quantity": 2}
                ]
            }
        )

        self.assertEqual(response.status_code, 400)
    def test_api_cut_exceeds_stock_length(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts": [
                    {"length": 25, "quantity": 2}
                ]
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Cut length exceeds stock length"
        )

    def test_quantity_validation(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts": [
                    {"length": 5, "quantity": 2.5}
                ]
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Invalid cut quantity"
        )
    def test_api_zero_quantity(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts": [
                    {"length": 5, "quantity": 0}
                ]
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Invalid cut quantity"
        )
    def test_api_invalid_cut_object(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts":[5,10,15]
            }
        )

        self.assertEqual(response.status_code, 400)
    def test_api_invalid_cuts_type(self):
        response = self.client.post(
            "/api/optimize",
            json={
                "stock_length": 20,
                "cuts": "hello"
            }
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json()["error"],
            "Cuts must be a list"
        )
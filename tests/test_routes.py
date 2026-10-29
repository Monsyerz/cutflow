import unittest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.extensions import db

class TestRoutes(unittest.TestCase):

    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
        })

        self.client = self.app.test_client()
    def test_database_rollback(self):

        with patch.object(
            db.session,
            "commit",
            side_effect=SQLAlchemyError("Simulated database failure")
        ), patch.object(db.session, "rollback") as mock_rollback:

            response = self.client.post("/", data={
                "stock_length": "20",
                "cut_length": "10",
                "quantity": "2"
            })

            mock_rollback.assert_called_once()

            self.assertEqual(response.status_code, 200)

            self.assertIn(
                b"Unable to save optimization results",
                response.data
            )       
    def test_empty_cuts(self):
        response = self.client.post("/", data={
            "stock_length": "20",
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Please enter at least one cut",
            response.data
        )
    def test_invalid_cut_length(self):
        response = self.client.post("/", data={
            "stock_length": "20",
            "cut_length": "invalid",
            "quantity": "2"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Cut length must be a valid number",
            response.data
        )


    def test_negative_cut_length(self):
        response = self.client.post("/", data={
            "stock_length": "20",
            "cut_length": "-10",
            "quantity": "2"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Cut lengths must be positive numbers",
            response.data)
        self.assertIn(
            b'value="20"',
            response.data
        )


    def test_cut_length_exceeds_stock_length(self):
        response = self.client.post("/", data={
            "stock_length": "20",
            "cut_length": "25",
            "quantity": "2"
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Cut lengths cannot exceed stock length",
            response.data
        )   

    def test_preserve_cut_values(self):
        response = self.client.post("/", data={
            "stock_length": "20",
            "cut_length": ["10", "25"],
            "quantity": ["2", "3"]
        })

        self.assertEqual(response.status_code, 200)

        self.assertIn(b'value="10"', response.data)
        self.assertIn(b'value="25"', response.data)
        self.assertIn(b'value="2"', response.data)
        self.assertIn(b'value="3"', response.data)
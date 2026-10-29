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
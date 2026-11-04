import unittest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from app.db_models import OptimizationResult

import csv
from datetime import datetime
from io import StringIO

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

        with self.app.app_context():
            db.create_all()
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()

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

    def test_csv_export(self):
        with self.app.app_context():

            result = OptimizationResult(
                stocks_used=2,
                waste=5.0,
                utilization=87.5
            )
            db.session.add(result)
            db.session.commit()
            response=self.client.get("/export")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"ID,Stocks Used,Waste,Utilization,Created At", response.data)
            self.assertIn(b"2,5.0,87.5", response.data)
            self.assertEqual(response.mimetype, "text/csv")
    
    def test_history_database_error(self):
        with patch(
            "flask_sqlalchemy.query.Query.all",
            side_effect=SQLAlchemyError("Simulated database failure")
        ):
            response = self.client.get("/history")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Unable to fetch optimization history",
            response.data
        )
        self.assertNotIn(b"No optimization history yet.", response.data)
        self.assertNotIn(b"Download CSV", response.data)

    def test_csv_export_database_error(self):
        with patch(
            "flask_sqlalchemy.query.Query.all",
            side_effect=SQLAlchemyError("Simulated database failure")
        ):
            response = self.client.get("/export")

        self.assertEqual(response.status_code, 503)
        self.assertIn(
            b"Unable to export optimization history",
            response.data
        )
        self.assertEqual(response.mimetype, "text/html")
        self.assertNotIn("Content-Disposition", response.headers)
        self.assertNotIn(b"No optimization history yet.", response.data)
        self.assertNotIn(b"Download CSV", response.data)


    def test_home_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Cut Optimizer", response.data)

    def test_invalid_stock_lengths(self):
        cases = [
            (None, b"Please enter a valid stock length."),
            ("", b"Please enter a valid stock length."),
            ("abc", b"Stock length must be a valid number."),
            ("0", b"Stock length must be a positive number."),
            ("-20", b"Stock length must be a positive number."),
            ("nan", b"Stock length must be a positive number."),
            ("inf", b"Stock length must be a positive number."),
            ("-inf", b"Stock length must be a positive number.")
        ]

        for value, message in cases:
            with self.subTest(stock_length=value):
                data = {
                    "cut_length": "10",
                    "quantity": "2"
                }

                if value is not None:
                    data["stock_length"] = value

                response = self.client.post("/", data=data)

                self.assertEqual(response.status_code, 200)
                self.assertIn(message, response.data)

                with self.app.app_context():
                    self.assertEqual(
                        OptimizationResult.query.count(), 0
                    )

    def test_zero_and_non_finite_cut_lengths(self):
        for value in ["0", "nan", "inf", "-inf"]:
            with self.subTest(cut_length=value):
                response = self.client.post("/", data={
                    "stock_length": "20",
                    "cut_length": value,
                    "quantity": "2"
                })

                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    b"Cut lengths must be positive numbers.",
                    response.data
                )

                with self.app.app_context():
                    self.assertEqual(
                        OptimizationResult.query.count(), 0
                    )

    def test_invalid_quantities(self):
        conversion_error = (
            b"Cut length must be a valid number "
            b"and quantity must be a whole number."
        )

        cases = [
            ("0", b"Quantities must be positive integers."),
            ("-2", b"Quantities must be positive integers."),
            ("1.5", conversion_error),
            ("abc", conversion_error),
            ("", conversion_error)
        ]

        for value, message in cases:
            with self.subTest(quantity=value):
                response = self.client.post("/", data={
                    "stock_length": "20",
                    "cut_length": "10",
                    "quantity": value
                })

                self.assertEqual(response.status_code, 200)
                self.assertIn(message, response.data)

                with self.app.app_context():
                    self.assertEqual(
                        OptimizationResult.query.count(), 0
                    )

    def test_mismatched_cut_lengths_and_quantities(self):
        cases = [
            (["10", "5"], ["2"]),
            (["10"], ["2", "3"]),
            (["10"], [])
        ]

        for lengths, quantities in cases:
            with self.subTest(
                lengths=lengths,
                quantities=quantities
            ):
                response = self.client.post("/", data={
                    "stock_length": "20",
                    "cut_length": lengths,
                    "quantity": quantities
                })

                self.assertEqual(response.status_code, 200)
                self.assertIn(
                    b"Each cut length must have a quantity.",
                    response.data
                )

                with self.app.app_context():
                    self.assertEqual(
                        OptimizationResult.query.count(), 0
                    )


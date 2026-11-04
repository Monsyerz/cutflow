import unittest
from unittest.mock import patch
from sqlalchemy.exc import SQLAlchemyError
from app.db_models import OptimizationResult

import csv
from datetime import datetime, timedelta
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

    def test_successful_optimization_saves_result(self):
        response = self.client.post("/", data={
            "stock_length": "20",
            "cut_length": ["5", "15", "7", "10.5"],
            "quantity": ["2", "2", "1", "3"]
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Total Stocks: 5", response.data)
        self.assertIn(b"Total Cuts: 8", response.data)
        self.assertIn(b"Total Cut Length: 78.50", response.data)
        self.assertIn(b"Total Waste: 21.50", response.data)
        self.assertIn(b"Overall Utilization: 78.50%", response.data)

        with self.app.app_context():
            self.assertEqual(OptimizationResult.query.count(), 1)

            result = OptimizationResult.query.one()

            self.assertEqual(result.stocks_used, 5)
            self.assertAlmostEqual(result.waste, 21.5)
            self.assertAlmostEqual(result.utilization, 78.5)

    def test_cut_equal_to_stock_length(self):
        response = self.client.post("/", data={
            "stock_length": "20",
            "cut_length": "20",
            "quantity": "2"
        })

        self.assertEqual(response.status_code, 200)

        with self.app.app_context():
            result = OptimizationResult.query.one()

            self.assertEqual(result.stocks_used, 2)
            self.assertAlmostEqual(result.waste, 0)
            self.assertAlmostEqual(result.utilization, 100)


    def test_empty_history(self):
        response = self.client.get("/history")

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"No optimization history yet.",
            response.data
        )
        self.assertNotIn(b"Download CSV", response.data)
        self.assertNotIn(
            b"Unable to fetch optimization history",
            response.data
        )

    def test_history_shows_latest_ten_results(self):
        base_time = datetime(2026, 1, 1, 12, 0, 0)

        with self.app.app_context():
            # Newest inserted first to test date ordering.
            for index in reversed(range(12)):
                db.session.add(OptimizationResult(
                    stocks_used=index + 1,
                    waste=5.0,
                    utilization=75.0,
                    created_at=base_time + timedelta(minutes=index)
                ))

            db.session.commit()

            expected_ids = [
                result.id
                for result in OptimizationResult.query.order_by(
                    OptimizationResult.created_at.desc()
                ).all()
            ]

        response = self.client.get("/history")
        html = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Download CSV", html)
        self.assertEqual(html.count("<p>Run #"), 10)

        positions = []

        for result_id in expected_ids[:10]:
            marker = f"<p>Run #{result_id}</p>"
            self.assertIn(marker, html)
            positions.append(html.index(marker))

        self.assertEqual(positions, sorted(positions))

        for result_id in expected_ids[10:]:
            self.assertNotIn(f"<p>Run #{result_id}</p>", html)

    def test_csv_export_empty_database(self):
        response = self.client.get("/export")
        rows = list(csv.reader(
            StringIO(response.get_data(as_text=True))
        ))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertEqual(
            response.headers["Content-Disposition"],
            "attachment; filename=history.csv"
        )
        self.assertEqual(rows, [[
            "ID", "Stocks Used", "Waste", "Utilization", "Created At"
        ]])

    def test_csv_export_includes_all_results_newest_first(self):
        base_time = datetime(2026, 1, 1, 12, 0, 0)
        expected_rows = []

        with self.app.app_context():
            for index in reversed(range(12)):
                created_at = base_time + timedelta(minutes=index)

                result = OptimizationResult(
                    stocks_used=index + 1,
                    waste=2.5,
                    utilization=87.5,
                    created_at=created_at
                )

                db.session.add(result)
                db.session.flush()

                expected_rows.append([
                    str(result.id),
                    str(index + 1),
                    "2.5",
                    "87.5",
                    str(created_at)
                ])

            db.session.commit()

        response = self.client.get("/export")
        rows = list(csv.reader(
            StringIO(response.get_data(as_text=True))
        ))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertEqual(
            response.headers["Content-Disposition"],
            "attachment; filename=history.csv"
        )
        self.assertEqual(rows[0], [
            "ID", "Stocks Used", "Waste", "Utilization", "Created At"
        ])
        self.assertEqual(len(rows), 13)
        self.assertEqual(rows[1:], expected_rows)

from app.extensions import db
from datetime import datetime, timezone

class OptimizationResult(db.Model):
    __tablename__ = "optimization_results"

    id = db.Column(db.Integer, primary_key=True)
    stocks_used = db.Column(db.Integer)
    waste = db.Column(db.Float)
    utilization = db.Column(db.Float)
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
from app import db
from datetime import datetime


class SystemKV(db.Model):
    __tablename__ = 'system_kv'

    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MonthlyReport(db.Model):
    __tablename__ = 'monthly_report'

    id = db.Column(db.BigInteger, primary_key=True)
    period_year = db.Column(db.Integer, nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    scope = db.Column(db.String(20), nullable=False, default='global')  # global | user
    user_id = db.Column(db.BigInteger, nullable=True)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('period_year', 'period_month', 'scope', 'user_id', name='uq_monthly_report_period_scope'),
    )



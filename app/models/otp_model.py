from app.ext import db
from datetime import datetime, timedelta

class OTP(db.Model):
    __tablename__ = "otp_codes"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), nullable=False)
    otp_code = db.Column(db.String(6), nullable=False)
    expired_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
from app.ext import db
from datetime import datetime

class EventCategory(db.Model):
    __tablename__ = "event_categories"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    nama_kategori = db.Column(
        db.String(100),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
from app.ext import db
from datetime import datetime

class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    eo_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("event_categories.id"),
        nullable=False
    )

    nama_event = db.Column(
        db.String(200),
        nullable=False
    )

    deskripsi = db.Column(
        db.Text
    )

    banner = db.Column(
        db.String(255)
    )

    lokasi = db.Column(
        db.String(255),
        nullable=False
    )

    tanggal = db.Column(
        db.DateTime,
        nullable=False
    )

    harga = db.Column(
        db.Numeric(12,2),
        default=0
    )

    kuota = db.Column(
        db.Integer,
        default=0
    )

    total_peserta = db.Column(
        db.Integer,
        default=0
    )

    is_published = db.Column(
        db.Boolean,
        default=False
    )

    status = db.Column(
        db.String(20),
        default="draft"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
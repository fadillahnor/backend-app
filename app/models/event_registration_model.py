from app.ext import db
from datetime import datetime

class EventRegistration(db.Model):

    __tablename__ = "event_registrations"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id"),
        nullable=False
    )

    kategori_lomba = db.Column(
        db.String(100),
        nullable=False
    )

    nama_peserta = db.Column(
        db.String(100),
        nullable=False
    )

    email_peserta = db.Column(
        db.String(100),
        nullable=False
    )

    nama_bib = db.Column(
        db.String(100),
        nullable=False
    )
    bib_number = db.Column(
    db.String(50),
    unique=True
    )
    nohp_peserta = db.Column(
        db.String(20),
        nullable=False
    )

    alamat_peserta = db.Column(
        db.String(255),
        nullable=False
    )

    kota_peserta = db.Column(
        db.String(100),
        nullable=False
    )

    provinsi_peserta = db.Column(
        db.String(100),
        nullable=False
    )

    tanggal_lahir = db.Column(
        db.String(20),
        nullable=False
    )

    jenis_kelamin = db.Column(
        db.String(20),
        nullable=False
    )

    scan_wajah = db.Column(
        db.String(255)
    )

    ukuran_jersey = db.Column(
        db.String(50),
        nullable=False
    )

    golongan_darah = db.Column(
        db.String(10),
        nullable=False
    )

    nama_kontak_darurat = db.Column(
        db.String(100),
        nullable=False
    )

    nomor_kontak_darurat = db.Column(
        db.String(20),
        nullable=False
    )

    riwayat_penyakit = db.Column(
        db.Text
    )

    pernyataan_sehat = db.Column(
        db.String(10),
        nullable=False
    )

    bukti_pembayaran = db.Column(
        db.String(255)
    )
    bib_number = db.Column(
    db.String(50),
    unique=True
)

    reject_reason = db.Column(
    db.Text
)
    status = db.Column(
        db.String(30),
        default="pending_payment"
    )
    status_kehadiran = db.Column(
        db.String(30),
        default="belum_hadir"
    )
    scan_at = db.Column(
        db.DateTime,
        nullable=True
    )
    status_kehadiran_event = db.Column(
        db.String(30),
        default="belum_hadir"
    )
    checkin_event_at = db.Column(
        db.DateTime,
        nullable=True
    )
    reject_reason = db.Column(
    db.Text
    )
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    user = db.relationship(
        "User",
        backref="event_registrations",
        lazy="joined"
    )

    @staticmethod
    def get_registration(registration_id):
        return EventRegistration.query.get(registration_id)

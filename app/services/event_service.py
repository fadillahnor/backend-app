import os
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
import re

from app.models.event_model import Event
from app.models.event_category_model import EventCategory
from app.ext import db
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_banner_file(photo):
    if not allowed_file(photo.filename):
        raise ValueError("Format banner tidak didukung")

    ext = photo.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"banner_{uuid4().hex}.{ext}")

    upload_dir = BASE_DIR / "uploads" / "event"
    os.makedirs(upload_dir, exist_ok=True)

    filepath = upload_dir / filename
    photo.save(str(filepath))

    return os.path.join("uploads", "event", filename).replace('\\', '/')


def create_event(eo_id, data):

    required = [
        "category_id",
        "nama_event",
        "lokasi",
        "tanggal",
        "harga",
        "kuota"
    ]

    missing = [
        k for k in required
        if not data.get(k) and data.get(k) != 0
    ]

    if missing:
        raise ValueError(
            "Missing fields: %s" % ", ".join(missing)
        )

    tanggal_raw = data["tanggal"]

    try:
        tanggal = datetime.strptime(
            tanggal_raw,
            "%Y-%m-%d %H:%M:%S"
        )

    except Exception:

        try:
            tanggal = datetime.strptime(
                tanggal_raw,
                "%Y-%m-%d"
            )

        except Exception:
            raise ValueError(
                "Invalid tanggal format"
            )

    raw_harga = data["harga"]

    try:
        harga = float(raw_harga)

    except Exception:

        if isinstance(raw_harga, str):

            s = raw_harga.replace(
                "Rp", ""
            ).replace(
                "rp", ""
            ).strip()

            s = re.sub(
                r"[^\d\.,]",
                "",
                s
            )

            if "." in s and "," in s:
                s = s.replace(".", "")
                s = s.replace(",", ".")

            elif "." in s:
                s = s.replace(".", "")

            elif "," in s:
                s = s.replace(",", ".")

            try:
                harga = float(s)

            except Exception:
                raise ValueError(
                    "Invalid harga value"
                )

        else:
            raise ValueError(
                "Invalid harga value"
            )

    kuota = int(data["kuota"])
    category_id = int(data["category_id"])

    category = EventCategory.query.get(
        category_id
    )

    if not category:
        raise ValueError(
            "Kategori tidak ditemukan"
        )

    banner_path = None

    banner_file = data.get(
        "banner_file"
    )

    if banner_file:
        banner_path = save_banner_file(
            banner_file
        )

    event = Event(
        eo_id=eo_id,
        category_id=category_id,
        nama_event=data["nama_event"],
        deskripsi=data.get("deskripsi"),
        banner=banner_path,
        lokasi=data["lokasi"],
        tanggal=tanggal,
        harga=harga,
        kuota=kuota
    )

    db.session.add(event)
    db.session.commit()

    return event


# ================= UPDATE EVENT =================

def update_event(event, data):

    if data.get("category_id"):

        category = EventCategory.query.get(
            int(data["category_id"])
        )

        if not category:
            raise ValueError(
                "Kategori tidak ditemukan"
            )

        event.category_id = int(
            data["category_id"]
        )

    if data.get("nama_event"):
        event.nama_event = data["nama_event"]

    if data.get("deskripsi") is not None:
        event.deskripsi = data["deskripsi"]

    if data.get("lokasi"):
        event.lokasi = data["lokasi"]

    if data.get("tanggal"):

        try:
            event.tanggal = datetime.strptime(
                data["tanggal"],
                "%Y-%m-%d %H:%M:%S"
            )

        except Exception:

            try:
                event.tanggal = datetime.strptime(
                    data["tanggal"],
                    "%Y-%m-%d"
                )

            except Exception:
                raise ValueError(
                    "Format tanggal salah"
                )

    if data.get("harga"):

        try:
            event.harga = float(
                data["harga"]
            )

        except Exception:
            raise ValueError(
                "Harga tidak valid"
            )

    if data.get("kuota"):

        try:
            event.kuota = int(
                data["kuota"]
            )

        except Exception:
            raise ValueError(
                "Kuota tidak valid"
            )

    banner_file = data.get(
        "banner_file"
    )

    if banner_file:
        event.banner = save_banner_file(
            banner_file
        )

    db.session.commit()

    return event


# ================= GET EVENT =================

def get_events_by_eo(eo_id):

    return Event.query.filter_by(
        eo_id=eo_id
    ).all()


def get_event(event_id):

    return Event.query.get(
        event_id
    )


# ================= DELETE EVENT =================

def delete_event(event):

    db.session.delete(event)
    db.session.commit()


# ================= PUBLISH EVENT =================

def publish_event(event):

    event.is_published = True
    event.status = "aktif"

    db.session.commit()


# ================= DASHBOARD EO =================

from sqlalchemy import func


def dashboard_eo(eo_id):

    total_event = Event.query.filter_by(
        eo_id=eo_id
    ).count()

    total_peserta = db.session.query(
        func.sum(Event.total_peserta)
    ).filter(
        Event.eo_id == eo_id
    ).scalar() or 0

    pendapatan = db.session.query(
        func.sum(
            Event.harga * Event.total_peserta
        )
    ).filter(
        Event.eo_id == eo_id
    ).scalar() or 0

    event_aktif = Event.query.filter(
        Event.eo_id == eo_id,
        Event.status == "aktif"
    ).count()

    return {
        "total_event": total_event,
        "total_peserta": total_peserta,
        "pendapatan": float(pendapatan),
        "event_aktif": event_aktif
    }
import os
from pathlib import Path
from uuid import uuid4
from werkzeug.utils import secure_filename
from datetime import datetime
import re

from app.models.event_model import Event
from app.models.event_category_model import EventCategory
from app.ext import db
from datetime import datetime
from app.models.event_registration_model import EventRegistration
from sqlalchemy.orm import joinedload

REGISTRATION_KEY_MAP = {
    'kategoriLomba': 'kategori_lomba',
    'namaPeserta': 'nama_peserta',
    'emailPeserta': 'email_peserta',
    'namaBib': 'nama_bib',
    'nohpPeserta': 'nohp_peserta',
    'alamatPeserta': 'alamat_peserta',
    'kotaPeserta': 'kota_peserta',
    'provinsiPeserta': 'provinsi_peserta',
    'tanggalLahir': 'tanggal_lahir',
    'jenisKelamin': 'jenis_kelamin',
    'scanWajah': 'scan_wajah',
    'ukuranJersey': 'ukuran_jersey',
    'golonganDarah': 'golongan_darah',
    'namaKontakDarurat': 'nama_kontak_darurat',
    'nomorKontakDarurat': 'nomor_kontak_darurat',
    'riwayatPenyakit': 'riwayat_penyakit',
    'pernyataanSehat': 'pernyataan_sehat',
    'buktiPembayaran': 'bukti_pembayaran'
}

def camel_to_snake(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def normalize_registration_data(data):
    normalized = {}
    for key, value in data.items():
        normalized_key = REGISTRATION_KEY_MAP.get(key, camel_to_snake(key))
        normalized[normalized_key] = value
    return normalized


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


def save_scan_wajah_file(photo):
    if not allowed_file(photo.filename):
        raise ValueError("Format file scan wajah tidak didukung")

    ext = photo.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(f"scan_wajah_{uuid4().hex}.{ext}")

    upload_dir = BASE_DIR / "uploads" / "scan_wajah"
    os.makedirs(upload_dir, exist_ok=True)

    filepath = upload_dir / filename
    photo.save(str(filepath))

    return os.path.join("uploads", "scan_wajah", filename).replace('\\', '/')


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
        maps_url=data.get("maps_url"),
        fasilitas_peserta=data.get("fasilitas_peserta"),
        tanggal=tanggal,
        harga=harga,
        kuota=kuota,
        nomor_rekening=data.get("nomor_rekening"),
        jenis_bank=data.get("jenis_bank")
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

    # ================= TAMBAHAN BARU =================

    if data.get("maps_url"):
        event.maps_url = data["maps_url"]

    if data.get("fasilitas_peserta"):
        event.fasilitas_peserta = data["fasilitas_peserta"]

    if data.get("nomor_rekening") is not None:
        event.nomor_rekening = data["nomor_rekening"]

    if data.get("jenis_bank") is not None:
        event.jenis_bank = data["jenis_bank"]

    # =================================================

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

# ================= LIST EVENTS =================

def get_published_events():

    return (
        db.session.query(
            Event,
            EventCategory.nama_kategori
        )
        .join(
            EventCategory,
            Event.category_id == EventCategory.id
        )
        .filter(
            Event.is_published == True
        )
        .all()
    )

# ================= DETAIL EVENTS =================

def get_event_detail(event_id):

    return (
        db.session.query(
            Event,
            EventCategory.nama_kategori
        )
        .join(
            EventCategory,
            Event.category_id == EventCategory.id
        )
        .filter(
            Event.id == event_id,
            Event.is_published == True
        )
        .first()
    )


def get_event_registrations_by_eo(eo_id, event_id=None):
    query = (
        EventRegistration.query
        .join(Event, EventRegistration.event_id == Event.id)
        .options(joinedload(EventRegistration.user))
        .filter(Event.eo_id == eo_id)
    )

    if event_id is not None:
        query = query.filter(EventRegistration.event_id == event_id)

    return query.all()


# ================= SERVICE CHECKOUT =================
def register_event(user_id, event_id, data):

    data = normalize_registration_data(data or {})

    event = Event.query.get(event_id)

    if not event:
        raise ValueError("Event tidak ditemukan")

    required = [
        "kategori_lomba",
        "nama_peserta",
        "email_peserta",
        "nama_bib",
        "nohp_peserta",
        "alamat_peserta",
        "kota_peserta",
        "provinsi_peserta",
        "tanggal_lahir",
        "jenis_kelamin",
        "ukuran_jersey",
        "golongan_darah",
        "nama_kontak_darurat",
        "nomor_kontak_darurat",
        "pernyataan_sehat"
    ]

    missing = [
        field for field in required
        if not data.get(field) and data.get(field) != 0
    ]

    if missing:
        raise ValueError("Field(s) required: %s" % ", ".join(missing))

    existing_bib = EventRegistration.query.filter_by(
        event_id=event_id,
        nama_bib=data["nama_bib"]
    ).first()

    if existing_bib:
        raise ValueError("Nama BIB sudah digunakan untuk event ini")

    registration = EventRegistration(
        user_id=user_id,
        event_id=event_id,

        kategori_lomba=data["kategori_lomba"],
        nama_peserta=data["nama_peserta"],
        email_peserta=data["email_peserta"],
        nama_bib=data["nama_bib"],
        nohp_peserta=data["nohp_peserta"],
        alamat_peserta=data["alamat_peserta"],
        kota_peserta=data["kota_peserta"],
        provinsi_peserta=data["provinsi_peserta"],
        tanggal_lahir=data["tanggal_lahir"],
        jenis_kelamin=data["jenis_kelamin"],
        scan_wajah=data.get("scan_wajah"),
        ukuran_jersey=data["ukuran_jersey"],
        golongan_darah=data["golongan_darah"],
        nama_kontak_darurat=data["nama_kontak_darurat"],
        nomor_kontak_darurat=data["nomor_kontak_darurat"],
        riwayat_penyakit=data.get("riwayat_penyakit"),
        pernyataan_sehat=data["pernyataan_sehat"],

        status="pending_payment"
    )

    db.session.add(registration)
    db.session.commit()

    return registration


def get_registration(registration_id):
    return (
        EventRegistration.query
        .options(joinedload(EventRegistration.user))
        .filter_by(id=registration_id)
        .first()
    )


# ================= UPLOAD PAYMENT =================
def upload_payment(registration, photo):

    ext = photo.filename.rsplit(
        ".",
        1
    )[1].lower()

    filename = secure_filename(
        f"payment_{registration.id}.{ext}"
    )

    upload_dir = BASE_DIR / "uploads" / "payment"

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    filepath = upload_dir / filename

    photo.save(str(filepath))

    registration.bukti_pembayaran = (
        f"uploads/payment/{filename}"
    )

    registration.status = (
        "waiting_verification"
    )

    db.session.commit()

    return registration
def generate_bib_number(event_id):

    total = EventRegistration.query.filter_by(
        event_id=event_id
    ).count()

    nomor_urut = total + 1

    tahun = datetime.now().year

    return f"RUN-{tahun}-{event_id:03d}-{nomor_urut:04d}"

# ================= GENERATE BIB NUMBER =================
def generate_bib_number(event_id):

    total = EventRegistration.query.filter_by(
        event_id=event_id
    ).count()

    nomor_urut = total + 1

    tahun = datetime.now().year

    return f"RUN-{tahun}-{event_id:03d}-{nomor_urut:04d}"

# ================= APPROVE PAYMENT =================
def approve_payment(registration):

    bib_number = generate_bib_number(
        registration.event_id
    )

    registration.bib_number = bib_number

    registration.status = "paid"

    event = Event.query.get(
        registration.event_id
    )

    event.total_peserta += 1

    db.session.commit()

    return registration


# ================= REJECT PAYMENT =================
def reject_payment(
    registration,
    reason
):

    registration.status = "rejected"

    registration.reject_reason = reason

    db.session.commit()

    return registration


    # ================= MY REGISTRATIONS =================

def get_my_registrations(user_id):

    return (
        db.session.query(
            EventRegistration,
            Event
        )
        .join(
            Event,
            EventRegistration.event_id == Event.id
        )
        .filter(
            EventRegistration.user_id == user_id
        )
        .all()
    )
    # ================= DETAIL REGISTRATIONS =================

def get_registration_detail(registration_id):
    return (
        EventRegistration.query
        .join(
            Event,
            EventRegistration.event_id == Event.id
        )
        .add_entity(Event)
        .filter(
            EventRegistration.user_id == user_id
        )
        .all()
    )

def get_registration_detail(
    registration_id
):
    return (
        EventRegistration.query
        .options(
            joinedload(
                EventRegistration.user
            )
        )
        .filter_by(
            id=registration_id
        )
        .first()
    )
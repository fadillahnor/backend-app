from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from app.services.event_service import (
    create_event,
    get_events_by_eo,
    get_event,
    delete_event,
    update_event,
    get_event_detail,
    get_published_events,
    register_event,
    get_registration,
    upload_payment,
    save_scan_wajah_file
)

from app.decorators.eo_required import eo_required

event_bp = Blueprint(
    "event",
    __name__
)

@event_bp.route("/", methods=["POST"])
@jwt_required()
@eo_required()
def create():
    """
    Create Event (EO only)
    ---
    tags:
      - Event
    consumes:
      - multipart/form-data
    security:
      - Bearer: []
    parameters:
      - name: category_id
        in: formData
        required: true
        type: integer
      - name: nama_event
        in: formData
        required: true
        type: string
      - name: tanggal
        in: formData
        required: true
        type: string
        format: date
      - name: lokasi
        in: formData
        required: true
        type: string
      - name: deskripsi
        in: formData
        required: false
        type: string
      - name: harga
        in: formData
        required: true
        type: string
      - name: kuota
        in: formData
        required: true
        type: integer
      - name: banner
        in: formData
        required: false
        type: file
        description: File gambar banner (png, jpg, jpeg)
    responses:
      201:
        description: Event berhasil dibuat
      400:
        description: Input tidak valid atau error
    """

    eo_id = int(get_jwt_identity())

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()

    banner = request.files.get("banner")
    if banner:
        data["banner_file"] = banner

    required = ["category_id", "nama_event", "lokasi", "tanggal", "harga", "kuota"]
    missing = [f for f in required if not data.get(f) and data.get(f) != 0]
    if missing:
      return jsonify({"msg": "Field(s) required: %s" % ", ".join(missing)}), 400

    try:
      event = create_event(eo_id, data)
    except ValueError as exc:
      return jsonify({"msg": str(exc)}), 400

    return jsonify({
      "msg": "Event berhasil dibuat",
      "id": event.id
    }), 201

@event_bp.route("/", methods=["GET"])
@jwt_required()
@eo_required()
def get_all():
    """
    List EO Events (EO only)
    ---
    tags:
      - Event
    security:
      - Bearer: []
    responses:
      200:
        description: List event berhasil diambil
      401:
        description: Unauthorized - JWT token tidak valid atau tidak ada
    """

    eo_id = int(
        get_jwt_identity()
    )

    events = get_events_by_eo(
        eo_id
    )

    result = []

    for e in events:

        result.append({
            "id": e.id,
            "nama_event": e.nama_event,
            "status": e.status,
            "tanggal": str(e.tanggal),
            "banner": e.banner
        })

    return jsonify(result)

@event_bp.route("/<int:event_id>",
                methods=["DELETE"])
@jwt_required()
@eo_required()
def delete(event_id):
    """
    Delete Event (EO only)
    ---
    tags:
      - Event
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Event berhasil dihapus
      404:
        description: Event tidak ditemukan
    """

    event = get_event(event_id)

    if not event:
        return jsonify({
            "msg":"Event tidak ditemukan"
        }),404

    delete_event(event)

    return jsonify({
        "msg":"Event berhasil dihapus"
    })

@event_bp.route("/<int:event_id>", methods=["PUT"])
@jwt_required()
@eo_required()
def update(event_id):
    """
    Update Event (EO only)
    ---
    tags:
      - Event
    consumes:
      - multipart/form-data
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        required: true
        type: integer
      - name: category_id
        in: formData
        required: false
        type: integer
      - name: nama_event
        in: formData
        required: false
        type: string
      - name: tanggal
        in: formData
        required: false
        type: string
        format: date
      - name: lokasi
        in: formData
        required: false
        type: string
      - name: deskripsi
        in: formData
        required: false
        type: string
      - name: harga
        in: formData
        required: false
        type: string
      - name: kuota
        in: formData
        required: false
        type: integer
      - name: banner
        in: formData
        required: false
        type: file
        description: File gambar banner (png, jpg, jpeg)
    responses:
      200:
        description: Event berhasil diubah
      400:
        description: Input tidak valid atau error
      404:
        description: Event tidak ditemukan
    """

    event = get_event(event_id)
    if not event:
        return jsonify({"msg": "Event tidak ditemukan"}), 404

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()

    banner = request.files.get("banner")
    if banner:
        data["banner_file"] = banner

    try:
        event = update_event(event, data)
    except ValueError as exc:
        return jsonify({"msg": str(exc)}), 400

    return jsonify({
        "msg": "Event berhasil diubah",
        "event": {
            "id": event.id,
            "nama_event": event.nama_event,
            "lokasi": event.lokasi,
            "tanggal": str(event.tanggal),
            "banner": event.banner,
            "status": event.status
        }
    }), 200

@event_bp.route(
    "/publish/<int:event_id>",
    methods=["PUT"]
)
@jwt_required()
@eo_required()
def publish(event_id):

    event = get_event(event_id)

    if not event:
        return jsonify({
            "msg":"Event tidak ditemukan"
        }),404

    publish_event(event)

    return jsonify({
        "msg":"Event berhasil dipublish"
    })

@event_bp.route(
    "/dashboard",
    methods=["GET"]
)
@jwt_required()
@eo_required()
def dashboard():
    """
    EO Dashboard Data (EO only)
    ---
    tags:
      - Event
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard data berhasil diambil
      401:
        description: Unauthorized - JWT token tidak valid atau tidak ada
    """

    eo_id = int(
        get_jwt_identity()
    )

    data = dashboard_eo(eo_id)

    return jsonify(data), 200

@event_bp.route(
    "/list",
    methods=["GET"]
)
@jwt_required()
def list_event():
    """
    List Event Untuk User
    ---
    tags:
      - User Event
    security:
      - Bearer: []
    responses:
      200:
        description: Berhasil mengambil data event
    """

    events = get_published_events()

    result = []

    for event, kategori in events:

        result.append({
            "id": event.id,
            "nama_event": event.nama_event,
            "lokasi": event.lokasi,
            "tanggal": str(event.tanggal),
            "harga": float(event.harga),
            "kuota": event.kuota,
            "banner": event.banner,
            "kategori": kategori
        })

    return jsonify(result), 200

@event_bp.route(
    "/detail/<int:event_id>",
    methods=["GET"]
)
@jwt_required()
def detail_event(event_id):
    """
    Detail Event
    ---
    tags:
      - User Event
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Detail event
      404:
        description: Event tidak ditemukan
    """

    data = get_event_detail(event_id)

    if not data:
        return jsonify({
            "msg": "Event tidak ditemukan"
        }), 404

    event, kategori = data

    return jsonify({
        "id": event.id,
        "nama_event": event.nama_event,
        "banner": event.banner,
        "deskripsi": event.deskripsi,
        "kategori": kategori,
        "tanggal": str(event.tanggal),
        "lokasi": event.lokasi,
        "maps_url": event.maps_url,
        "harga": float(event.harga),
        "kuota": event.kuota,
        "total_peserta": event.total_peserta,
        "fasilitas_peserta": event.fasilitas_peserta,
        "status": event.status
    }), 200

@event_bp.route(
    "/register/<int:event_id>",
    methods=["POST"]
)
@jwt_required()
def register_event_user(event_id):
    """
    Register Event
    ---
    tags:
      - Event Registration
    consumes:
      - multipart/form-data
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        required: true
        type: integer
      - name: kategori_lomba
        in: formData
        required: true
        type: string
      - name: nama_peserta
        in: formData
        required: true
        type: string
      - name: email_peserta
        in: formData
        required: true
        type: string
      - name: nama_bib
        in: formData
        required: true
        type: string
      - name: nohp_peserta
        in: formData
        required: true
        type: string
      - name: alamat_peserta
        in: formData
        required: true
        type: string
      - name: kota_peserta
        in: formData
        required: true
        type: string
      - name: provinsi_peserta
        in: formData
        required: true
        type: string
      - name: tanggal_lahir
        in: formData
        required: true
        type: string
      - name: jenis_kelamin
        in: formData
        required: true
        type: string
      - name: scan_wajah
        in: formData
        required: true
        type: file
      - name: ukuran_jersey
        in: formData
        required: true
        type: string
      - name: golongan_darah
        in: formData
        required: true
        type: string
      - name: nama_kontak_darurat
        in: formData
        required: true
        type: string
      - name: nomor_kontak_darurat
        in: formData
        required: true
        type: string
      - name: riwayat_penyakit
        in: formData
        required: false
        type: string
      - name: pernyataan_sehat
        in: formData
        required: true
        type: string
    responses:
      201:
        description: Berhasil daftar event
    """

    user_id = int(
        get_jwt_identity()
    )

    if request.is_json:
        data = request.get_json() or {}
    else:
        data = request.form.to_dict()

    scan_wajah = request.files.get("scan_wajah")
    if scan_wajah:
        data["scan_wajah"] = save_scan_wajah_file(scan_wajah)

    registration = register_event(
        user_id,
        event_id,
        data
    )

    return jsonify({
        "msg": "Pendaftaran berhasil",
        "registration_id": registration.id
    }), 201 

@event_bp.route(
    "/payment/<int:registration_id>",
    methods=["PUT"]
)
@jwt_required()
def upload_payment_proof(
    registration_id
):
    """
    Upload Bukti Pembayaran
    ---
    tags:
      - Event Registration
    consumes:
      - multipart/form-data
    security:
      - Bearer: []
    parameters:
      - name: registration_id
        in: path
        required: true
        type: integer
      - name: bukti
        in: formData
        type: file
        required: true
    responses:
      200:
        description: Upload berhasil
    """

    registration = get_registration(
        registration_id
    )

    if not registration:
        return jsonify({
            "msg": "Data tidak ditemukan"
        }), 404

    photo = request.files.get(
        "bukti"
    )

    if not photo:
        return jsonify({
            "msg": "File wajib diupload"
        }), 400

    upload_payment(
        registration,
        photo
    )

    return jsonify({
        "msg": "Bukti pembayaran berhasil diupload",
        "status": "waiting_verification"
    }), 200
from flask import Blueprint
from flask import request
from flask import jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from app.services.event_service import *

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

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.ext import db
from app.models.user_model import User
from app.models.event_model import Event
from app.models.event_registration_model import EventRegistration
from app.models.event_category_model import EventCategory
from app.decorators.superadmin_required import superadmin_required

admin_bp = Blueprint("admin", __name__)


# ─── GET /admin/dashboard ─────────────────────────────────────────────────────
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@superadmin_required()
def admin_dashboard():
    """
    Super Admin Dashboard Stats
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard stats
    """
    total_users        = User.query.filter(User.role == 1).count()
    total_eo           = User.query.filter(User.role == 2).count()
    total_events       = Event.query.count()
    total_published    = Event.query.filter_by(is_published=True).count()
    total_pending      = Event.query.filter_by(status="pending_approval").count()
    total_registrasi   = EventRegistration.query.count()

    return jsonify({
        "total_users":      total_users,
        "total_eo":         total_eo,
        "total_events":     total_events,
        "total_published":  total_published,
        "total_pending":    total_pending,
        "total_registrasi": total_registrasi,
    }), 200


# ─── GET /admin/events ────────────────────────────────────────────────────────
@admin_bp.route("/events", methods=["GET"])
@jwt_required()
@superadmin_required()
def admin_list_events():
    """
    Super Admin — List All Events
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Semua event
    """
    events = Event.query.order_by(Event.created_at.desc()).all()

    result = []
    for e in events:
        eo = User.query.get(e.eo_id)
        cat = EventCategory.query.get(e.category_id)
        result.append({
            "id":           e.id,
            "nama_event":   e.nama_event,
            "lokasi":       e.lokasi,
            "tanggal":      str(e.tanggal),
            "harga":        float(e.harga or 0),
            "kuota":        e.kuota,
            "is_published": e.is_published,
            "status":       e.status,
            "banner":       e.banner,
            "eo_nama":      eo.nama if eo else "-",
            "kategori":     cat.nama_kategori if cat else "-",
            "created_at":   str(e.created_at),
        })

    return jsonify(result), 200


# ─── PUT /admin/events/<id>/approve ───────────────────────────────────────────
@admin_bp.route("/events/<int:event_id>/approve", methods=["PUT"])
@jwt_required()
@superadmin_required()
def admin_approve_event(event_id):
    """
    Super Admin — Approve Event
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Event diapprove
      404:
        description: Event tidak ditemukan
    """
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"msg": "Event tidak ditemukan"}), 404

    event.is_published = True
    event.status = "published"
    db.session.commit()

    return jsonify({"msg": "Event berhasil di-approve dan dipublish"}), 200


# ─── PUT /admin/events/<id>/reject ────────────────────────────────────────────
@admin_bp.route("/events/<int:event_id>/reject", methods=["PUT"])
@jwt_required()
@superadmin_required()
def admin_reject_event(event_id):
    """
    Super Admin — Reject Event
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - name: event_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Event direject
      404:
        description: Event tidak ditemukan
    """
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"msg": "Event tidak ditemukan"}), 404

    event.is_published = False
    event.status = "rejected"
    db.session.commit()

    return jsonify({"msg": "Event ditolak"}), 200


# ─── GET /admin/users ─────────────────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@superadmin_required()
def admin_list_users():
    """
    Super Admin — List All Users
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Semua user
    """
    users = User.query.order_by(User.created_at.desc()).all()

    result = []
    for u in users:
        result.append({
            "id":          u.id,
            "nama":        u.nama,
            "username":    u.username,
            "email":       u.email,
            "role":        u.role,
            "role_name":   u.role_name,
            "is_verified": u.is_verified,
            "created_at":  str(u.created_at),
        })

    return jsonify(result), 200

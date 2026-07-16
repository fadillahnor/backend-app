from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.auth_service import (
    register_user,
    verify_otp,
    login_user
)

from app.services.profile_service import update_profile
from app.models.user_model import User
from app.models.event_registration_model import EventRegistration

auth_bp = Blueprint("auth", __name__)

# ================= REGISTER =================
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register User + Kirim OTP
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
            password:
              type: string
            nama:
              type: string
            username:
              type: string
            role:
              type: integer
              description: Role user (1=USER, 2=EO)
            tgl_lahir:
              type: string
              format: date
            nohp:
              type: string
            alamat:
              type: string
    responses:
      201:
        description: Register berhasil
      400:
        description: Email sudah digunakan atau error
    """
    data = request.get_json() or {}

    required_fields = ["email", "password", "nama", "username"]
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return jsonify({"msg": "Field(s) required: %s" % ", ".join(missing_fields)}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email sudah digunakan"}), 400

    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "Username sudah digunakan"}), 400

    from sqlalchemy.exc import IntegrityError
    try:
        user = register_user(data)
    except ValueError as exc:
        return jsonify({"msg": str(exc)}), 400
    except IntegrityError:
        return jsonify({"msg": "Username atau Email sudah terdaftar"}), 400
    except Exception as exc:
        return jsonify({"msg": f"Terjadi kesalahan server: {str(exc)}"}), 500

    return jsonify({
        "msg": "Register berhasil, cek email untuk OTP",
        "user_id": user.id
    }), 201


# ================= VERIFY OTP =================
@auth_bp.route("/verify-otp", methods=["POST"])
def verify():
    """
    Verifikasi OTP
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
            otp:
              type: string
    responses:
      200:
        description: OTP terverifikasi
      400:
        description: OTP tidak valid
    """
    data = request.get_json()

    success, message = verify_otp(
        data["email"],
        data["otp"]
    )

    if not success:
        return jsonify({
            "msg": message
        }), 400

    return jsonify({
        "msg": message
    }), 200


# ================= LOGIN =================
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login User (JWT)
    ---
    tags:
      - Auth
    parameters:
      - name: body
        in: body
        required: true
        schema:
          properties:
            email:
              type: string
            password:
              type: string
            role:
              type: integer
              description: Role login (1=USER, 2=EO, 3=SUPER_ADMIN). Optional for SUPER_ADMIN only.
    responses:
      200:
        description: Login berhasil
      400:
        description: Email atau password salah
    """
    data = request.get_json() or {}
    result, error = login_user(data)

    if error:
        return jsonify({
            "msg": error
        }), 400

    return jsonify({
    "msg": "Login berhasil",
    "access_token": result["token"],
    "role": result["role"],
    "user_id": result["user_id"],
    "nama": result["nama"]
}), 200


# ================= GET PROFILE =================
@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """
    Get User Profile (JWT Required)
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    responses:
      200:
        description: Profile berhasil diambil
      401:
        description: Unauthorized - JWT token tidak valid atau tidak ada
      404:
        description: User tidak ditemukan
    """
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "msg": "User tidak ditemukan"
        }), 404

    return jsonify({
    "id": user.id,
    "nama": user.nama,
    "username": user.username,
    "email": user.email,
    "role": user.role,
    "role_name": user.role_name,
    "tgl_lahir": str(user.tgl_lahir) if user.tgl_lahir else None,
    "nohp": user.nohp,
    "alamat": user.alamat,
    "foto_profile": user.foto_profile,
    "is_verified": user.is_verified,
    "created_at": user.created_at.isoformat()
}), 200


# ================= GET ME =================
@auth_bp.route("/me", methods=["GET", "OPTIONS"])
@jwt_required(optional=True)
def get_me():
    if request.method == "OPTIONS":
        return jsonify({}), 200

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"msg": "Unauthorized"}), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({
            "msg": "User tidak ditemukan"
        }), 404

    registrations = EventRegistration.query.filter_by(user_id=user_id).all()

    registration_data = [
        {
            "id": r.id,
            "event_id": r.event_id,
            "status": r.status,
            "bib_number": r.bib_number,
            "nama_bib": r.nama_bib,
            "bukti_pembayaran": r.bukti_pembayaran,
            "reject_reason": r.reject_reason,
            "created_at": r.created_at.isoformat()
        }
        for r in registrations
    ]

    # Combine user data and latest registration status
    latest_registration = registrations[-1] if registrations else None

    return jsonify({
        "id": user.id,
        "nama": user.nama,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "role_name": user.role_name,
        "tgl_lahir": str(user.tgl_lahir) if user.tgl_lahir else None,
        "nohp": user.nohp,
        "alamat": user.alamat,
        "foto_profile": user.foto_profile,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat(),
        "registrations": registration_data,
        "payment_verified": latest_registration.status in ["paid", "approved"] if latest_registration else None,
        "bib_number": latest_registration.bib_number if latest_registration else None,
        "registration_status": latest_registration.status if latest_registration else None
    }), 200


# ================= EDIT PROFILE =================
@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def edit_profile():
    """
    Edit User Profile (JWT Required)
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    consumes:
      - multipart/form-data
    parameters:
      - name: nama
        in: formData
        type: string
        required: false
        description: Nama lengkap
      - name: username
        in: formData
        type: string
        required: false
        description: Username
      - name: email
        in: formData
        type: string
        required: false
        description: Email
      - name: tgl_lahir
        in: formData
        type: string
        format: date
        required: false
        description: Tanggal lahir (YYYY-MM-DD)
      - name: nohp
        in: formData
        type: string
        required: false
        description: Nomor HP
      - name: alamat
        in: formData
        type: string
        required: false
        description: Alamat
      - name: foto_profile
        in: formData
        type: file
        required: false
        description: Foto profil
    responses:
      200:
        description: Profil berhasil diperbarui
      400:
        description: Error updating profile
      401:
        description: Unauthorized - JWT token tidak valid atau tidak ada
    """
    user_id = get_jwt_identity()

    data = request.form

    photo = request.files.get("foto_profile")

    user, error = update_profile(
        user_id,
        data,
        photo
    )

    if error:
        return jsonify({
            "msg": error
        }), 400

    return jsonify({
        "msg": "Profil berhasil diperbarui",
        "data": {
            "id": user.id,
            "nama": user.nama,
            "username": user.username,
            "email": user.email,
            "tgl_lahir": str(user.tgl_lahir) if user.tgl_lahir else None,
            "nohp": user.nohp,
            "alamat": user.alamat,
            "foto_profile": user.foto_profile
        }
    }), 200
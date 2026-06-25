from flask import Blueprint, request, jsonify
from app.services.auth_service import register_user, verify_otp, login_user
from app.models.user_model import User

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
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - nama
            - username
            - email
            - password
          properties:
            nama:
              type: string
              example: Budi
            username:
              type: string
              example: budi123
            email:
              type: string
              example: budi@email.com
            password:
              type: string
              example: 123456
            tgl_lahir:
              type: string
              example: 2000-01-01
            nohp:
              type: string
              example: 08123456789
            alamat:
              type: string
              example: Jakarta
    responses:
      201:
        description: Register berhasil, OTP dikirim
    """
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Email sudah digunakan"}), 400

    user = register_user(data)

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
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - otp
          properties:
            email:
              type: string
              example: user@email.com
            otp:
              type: string
              example: 123456
    responses:
      200:
        description: OTP valid
    """
    data = request.get_json()

    success, message = verify_otp(data["email"], data["otp"])

    if not success:
        return jsonify({"msg": message}), 400

    return jsonify({"msg": message}), 200


# ================= LOGIN =================
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login User (JWT)
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: user@email.com
            password:
              type: string
              example: 123456
    responses:
      200:
        description: Login berhasil
    """
    data = request.get_json()

    token, error = login_user(data)

    if error:
        return jsonify({"msg": error}), 400

    return jsonify({
        "msg": "Login berhasil",
        "access_token": token
    }), 200
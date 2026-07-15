from app.models.user_model import User
from app.models.otp_model import OTP
from app.ext import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app.utils.otp import generate_otp
from app.utils.email import send_otp_email


def register_user(data):
    # Validasi dan konversi password ke string
    password = str(data["password"]).strip()
    if not password or len(password) < 6:
        raise ValueError("Password harus minimal 6 karakter")
    
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    otp_code = generate_otp()
    expired = datetime.utcnow() + timedelta(minutes=5)

    role = int(data.get("role", 1))
    if role not in [1, 2]:
        raise ValueError(
            "Role register hanya User(1) atau EO(2)"
    )

    user = User(
    nama=data["nama"],
    username=data["username"],
    password=hashed_password,
    email=data["email"],
    tgl_lahir=data.get("tgl_lahir"),
    nohp=data.get("nohp"),
    alamat=data.get("alamat"),
    role=role,
    is_verified=False
)

    otp = OTP(
        email=data["email"],
        otp_code=otp_code,
        expired_at=expired
    )

    try:
        db.session.add_all([user, otp])
        db.session.flush()
        send_otp_email(user.email, otp_code)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return user


def verify_otp(email, otp_input):
    otp = OTP.query.filter_by(email=email, otp_code=otp_input).first()

    if not otp:
        return False, "OTP salah"

    if otp.expired_at < datetime.utcnow():
        return False, "OTP expired"

    user = User.query.filter_by(email=email).first()
    user.is_verified = True

    db.session.delete(otp)
    db.session.commit()

    return True, "Verifikasi berhasil"

def login_user(data):

    email = data.get("email")
    password = str(data.get("password", "")).strip()

    if not email:
        return None, "Email harus diisi"

    if not password:
        return None, "Password tidak boleh kosong"

    # Find the user by email regardless of role
    user = User.query.filter_by(email=email).first()
    if not user:
        return None, "User tidak ditemukan"

    if not check_password_hash(user.password, password):
        # Legacy support: if password is stored in plain text, allow exact match
        if user.password != password:
            return None, "Password salah"

    if not user.is_verified:
        return None, "User belum verifikasi OTP"

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "role": user.role
        }
    )

    return {
        "token": token,
        "role": user.role,
        "user_id": user.id,
        "nama": user.nama
    }, None
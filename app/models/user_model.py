from app.ext import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    tgl_lahir = db.Column(db.Date)
    nohp = db.Column(db.String(20))
    alamat = db.Column(db.Text)

    foto_profile = db.Column(db.String(255), nullable=True)
    role = db.Column(
    db.Integer,
    nullable=False,
    default=1
)

    is_verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, nama, username, password, email, tgl_lahir=None,
                 nohp=None, alamat=None, foto_profile=None, role=1, is_verified=False):
        self.nama = nama
        self.username = username
        self.password = password
        self.email = email
        self.tgl_lahir = tgl_lahir
        self.nohp = nohp
        self.alamat = alamat
        self.foto_profile = foto_profile
        self.role = role
        self.is_verified = is_verified

    @property
    def role_name(self):
        roles = {
            1: "USER",
            2: "EO",
            3: "SUPER_ADMIN"
        }

        return roles.get(self.role, "UNKNOWN")
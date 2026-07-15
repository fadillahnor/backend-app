import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    # ================= DATABASE =================
    db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    elif db_url.startswith("mysql://"):
        db_url = db_url.replace("mysql://", "mysql+pymysql://", 1)
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ================= JWT =================
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)

    # ================= EMAIL =================
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv("EMAIL_USER")
    MAIL_PASSWORD = os.getenv("EMAIL_PASS")
    MAIL_DEFAULT_SENDER = os.getenv("EMAIL_USER")

    # ================= SECURITY =================
    JSON_SORT_KEYS = False

    # ================= UPLOAD =================
    UPLOAD_FOLDER = "uploads/profile"
    EVENT_UPLOAD_FOLDER = "uploads/event"
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
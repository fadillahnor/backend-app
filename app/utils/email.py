import socket
from flask_mail import Message
from app.ext import mail

# --- PATCH SOCKET UNTUK MEMAKSA IPv4 (Fix Railway SMTP IPv6) ---
original_getaddrinfo = socket.getaddrinfo

def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
    # Paksa family menjadi AF_INET (IPv4)
    return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

# Terapkan patch secara global
socket.getaddrinfo = getaddrinfo_ipv4
# ---------------------------------------------------------------

def send_otp_email(to_email, otp):
    """
    Kirim OTP via SMTP dengan memaksa koneksi IPv4 (port 587).
    """
    msg = Message(
        subject="Kode OTP Verifikasi - RunTrack",
        recipients=[to_email],
        body=(
            f"Halo!\n\n"
            f"Kode OTP verifikasi akun RunTrack kamu adalah:\n\n"
            f"  {otp}\n\n"
            f"Kode berlaku selama 5 menit.\n\n"
            f"Jika kamu tidak merasa mendaftar, abaikan email ini.\n\n"
            f"- Tim RunTrack"
        )
    )
    
    try:
        mail.send(msg)
    except Exception as exc:
        raise RuntimeError(f"Gagal mengirim OTP via SMTP: {exc}")
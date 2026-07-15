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
    print(f"[EMAIL] Menyiapkan pengiriman OTP ke {to_email}...")
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
    
    # Set socket timeout agar tidak hang selamanya (mencegah 502 Bad Gateway)
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(10.0)
    
    try:
        print("[EMAIL] Mengirim email menggunakan Flask-Mail (SMTP)...")
        mail.send(msg)
        print("[EMAIL] Email berhasil dikirim!")
    except Exception as exc:
        print(f"[EMAIL] ERROR: Gagal mengirim email: {exc}")
        raise RuntimeError(f"Gagal mengirim OTP via SMTP: {exc}. Catatan: Railway memblokir port SMTP (25, 465, 587) secara default untuk akun baru.")
    finally:
        socket.setdefaulttimeout(original_timeout)
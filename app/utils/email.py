import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_otp_email(to_email, otp):
    """Kirim OTP via Gmail SMTP.
    Bekerja di Dokploy karena server Dokploy tidak memblokir port SMTP.
    
    Set environment variables:
      EMAIL_USER = gmail_kamu@gmail.com
      EMAIL_PASS = App Password 16 karakter (bukan password Gmail biasa)
    
    Cara buat App Password Gmail:
      1. Aktifkan 2FA: myaccount.google.com/security
      2. Buat App Password: myaccount.google.com/apppasswords
    """
    sender  = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        raise RuntimeError(
            "Gagal mengirim OTP: EMAIL_USER dan EMAIL_PASS harus di-set "
            "di environment variables."
        )

    msg = EmailMessage()
    msg["Subject"] = "Kode OTP Verifikasi - RunTrack"
    msg["From"]    = f"RunTrack <{sender}>"
    msg["To"]      = to_email
    msg.set_content(
        f"Halo!\n\n"
        f"Kode OTP verifikasi akun RunTrack kamu adalah:\n\n"
        f"  {otp}\n\n"
        f"Kode berlaku selama 5 menit.\n\n"
        f"Jika kamu tidak merasa mendaftar, abaikan email ini.\n\n"
        f"- Tim RunTrack"
    )

    # Coba port 587 (STARTTLS) dulu, fallback ke 465 (SSL)
    errors = []

    # Port 587 — STARTTLS
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.ehlo()
            s.login(sender, password)
            s.send_message(msg)
        return  # Berhasil
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(
            f"Gmail Auth gagal: pastikan EMAIL_PASS adalah App Password "
            f"16 karakter dari myaccount.google.com/apppasswords. Error: {exc}"
        ) from exc
    except Exception as exc:
        errors.append(f"port 587: {exc}")

    # Port 465 — SSL
    try:
        ctx = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=20) as s:
            s.login(sender, password)
            s.send_message(msg)
        return  # Berhasil
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(
            f"Gmail Auth gagal: pastikan EMAIL_PASS adalah App Password "
            f"16 karakter dari myaccount.google.com/apppasswords. Error: {exc}"
        ) from exc
    except Exception as exc:
        errors.append(f"port 465: {exc}")

    raise RuntimeError(f"Gagal kirim OTP via Gmail SMTP: {'; '.join(errors)}")
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_otp_email(to_email, otp):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        raise RuntimeError("Gagal mengirim email OTP: EMAIL_USER atau EMAIL_PASS tidak terkonfigurasi.")

    msg = EmailMessage()
    msg["Subject"] = "Kode OTP Verifikasi"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(f"Kode OTP kamu adalah: {otp}")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender, password)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        error_text = exc.smtp_error.decode(errors='ignore') if isinstance(exc.smtp_error, bytes) else exc.smtp_error
        raise RuntimeError(
            f"Gagal mengirim email OTP: SMTP AuthenticationError ({exc.smtp_code}) {error_text}. "
            "Periksa EMAIL_USER dan EMAIL_PASS, dan gunakan Gmail App Password jika perlu."
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal mengirim email OTP: {exc}") from exc
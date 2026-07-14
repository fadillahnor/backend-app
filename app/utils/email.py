import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_otp_email(to_email, otp):
    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        raise RuntimeError("Gagal mengirim email OTP: EMAIL_USER atau EMAIL_PASS tidak terkonfigurasi.")

    msg = EmailMessage()
    msg["Subject"] = "Kode OTP Verifikasi - RunTrack"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        f"Halo!\n\nKode OTP verifikasi akun RunTrack kamu adalah:\n\n"
        f"  {otp}\n\n"
        f"Kode berlaku selama 5 menit.\n\n"
        f"Jika kamu tidak merasa mendaftar, abaikan email ini.\n\n"
        f"- Tim RunTrack"
    )

    # Coba port 465 (SSL) terlebih dahulu — lebih sering dibuka di cloud hosting
    errors = []

    for attempt, (port, use_ssl) in enumerate([(465, True), (587, False)]):
        try:
            if use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context, timeout=20) as server:
                    server.login(sender, password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=20) as server:
                    server.ehlo()
                    server.starttls()
                    server.ehlo()
                    server.login(sender, password)
                    server.send_message(msg)
            return  # sukses
        except smtplib.SMTPAuthenticationError as exc:
            error_text = exc.smtp_error.decode(errors='ignore') if isinstance(exc.smtp_error, bytes) else str(exc.smtp_error)
            raise RuntimeError(
                f"Gagal mengirim email OTP: SMTP AuthenticationError ({exc.smtp_code}) {error_text}. "
                "Periksa EMAIL_USER dan EMAIL_PASS, gunakan Gmail App Password."
            ) from exc
        except Exception as exc:
            errors.append(f"Port {port}: {exc}")
            continue

    raise RuntimeError(f"Gagal mengirim email OTP (semua port gagal): {'; '.join(errors)}")
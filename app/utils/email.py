import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()


def send_otp_email(to_email, otp):
    smtp_user = os.getenv("EMAIL_USER")
    smtp_pass = os.getenv("EMAIL_PASS")
    api_key   = os.getenv("RESEND_API_KEY")

    # Utamakan Gmail SMTP jika EMAIL_USER + EMAIL_PASS tersedia (gratis, tanpa domain)
    if smtp_user and smtp_pass:
        _send_via_smtp(to_email, otp)
    elif api_key:
        # Fallback ke Resend jika tidak ada SMTP credentials
        # (Butuh domain terverifikasi di resend.com/domains agar bisa kirim ke semua email)
        sender_email = smtp_user or "onboarding@resend.dev"
        _send_via_resend(api_key, sender_email, to_email, otp)
    else:
        raise RuntimeError(
            "Gagal mengirim OTP: Tidak ada EMAIL_USER/EMAIL_PASS maupun RESEND_API_KEY."
        )


def _send_via_resend(api_key, sender_email, to_email, otp):
    payload = json.dumps({
        "from": f"RunTrack <{sender_email}>",
        "to": [to_email],
        "subject": "Kode OTP Verifikasi - RunTrack",
        "text": (
            f"Halo!\n\n"
            f"Kode OTP verifikasi akun RunTrack kamu adalah:\n\n"
            f"  {otp}\n\n"
            f"Kode berlaku selama 5 menit.\n\n"
            f"Jika kamu tidak merasa mendaftar, abaikan email ini.\n\n"
            f"- Tim RunTrack"
        ),
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status not in (200, 201):
                body = resp.read().decode()
                raise RuntimeError(f"Resend API error {resp.status}: {body}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="ignore")
        raise RuntimeError(f"Gagal kirim OTP via Resend: {exc.code} {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal kirim OTP via Resend: {exc}") from exc


def _send_via_smtp(to_email, otp):
    """Gmail SMTP — gratis, bekerja di Railway maupun lokal.
    Syarat: EMAIL_USER=gmail_kamu@gmail.com, EMAIL_PASS=App Password 16 karakter.
    Cara buat App Password: myaccount.google.com/apppasswords (aktifkan 2FA dulu).
    """
    import smtplib
    import ssl
    from email.message import EmailMessage

    sender = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not sender or not password:
        raise RuntimeError(
            "Gagal mengirim OTP: RESEND_API_KEY tidak ada dan "
            "EMAIL_USER/EMAIL_PASS tidak terkonfigurasi."
        )

    msg = EmailMessage()
    msg["Subject"] = "Kode OTP Verifikasi - RunTrack"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(f"Kode OTP kamu adalah: {otp}\n\nBerlaku 5 menit.")

    errors = []
    for port, use_ssl in [(465, True), (587, False)]:
        try:
            if use_ssl:
                ctx = ssl.create_default_context()
                with smtplib.SMTP_SSL("smtp.gmail.com", port, context=ctx, timeout=20) as s:
                    s.login(sender, password)
                    s.send_message(msg)
            else:
                with smtplib.SMTP("smtp.gmail.com", port, timeout=20) as s:
                    s.ehlo()
                    s.starttls()
                    s.ehlo()
                    s.login(sender, password)
                    s.send_message(msg)
            return
        except smtplib.SMTPAuthenticationError as exc:
            raise RuntimeError(f"SMTP Auth gagal: {exc}") from exc
        except Exception as exc:
            errors.append(f"port {port}: {exc}")

    raise RuntimeError(f"Semua SMTP port gagal: {'; '.join(errors)}")
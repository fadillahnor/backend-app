import os
import smtplib
import ssl
import json
import urllib.request
import urllib.error
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


def send_otp_email(to_email, otp):
    brevo_api  = os.getenv("BREVO_API_KEY")
    brevo_user = os.getenv("BREVO_SMTP_USER")   # b21081001@smtp-brevo.com
    brevo_pass = os.getenv("BREVO_SMTP_PASS")   # password dari tab SMTP Settings

    # Prioritas 1: Brevo HTTP API (jika BREVO_API_KEY di-set)
    if brevo_api:
        sender = os.getenv("EMAIL_USER", "noreply@runtrack.com")
        _send_via_brevo_api(brevo_api, sender, to_email, otp)

    # Prioritas 2: Brevo SMTP Relay (smtp-relay.brevo.com:587)
    # Tidak diblokir Railway karena bukan smtp.gmail.com
    elif brevo_user and brevo_pass:
        _send_via_brevo_smtp(brevo_user, brevo_pass, to_email, otp)

    else:
        raise RuntimeError(
            "Gagal mengirim OTP: Tambahkan BREVO_SMTP_USER dan BREVO_SMTP_PASS "
            "dari tab 'SMTP Settings' di app.brevo.com/transactional/email/real-time, "
            "atau tambahkan BREVO_API_KEY dari tab 'API Settings'."
        )


def _send_via_brevo_smtp(brevo_user, brevo_pass, to_email, otp):
    """Brevo SMTP Relay — gratis 300 email/hari, bekerja di Railway.
    Credentials dari: app.brevo.com > Transactional > Email > Real time > SMTP Settings
      BREVO_SMTP_USER = login (contoh: b21081001@smtp-brevo.com)
      BREVO_SMTP_PASS = password yang tertera
    """
    sender_name  = "RunTrack"
    sender_email = os.getenv("EMAIL_USER", brevo_user)

    msg = EmailMessage()
    msg["Subject"] = "Kode OTP Verifikasi - RunTrack"
    msg["From"]    = f"{sender_name} <{sender_email}>"
    msg["To"]      = to_email
    msg.set_content(
        f"Halo!\n\n"
        f"Kode OTP verifikasi akun RunTrack kamu adalah:\n\n"
        f"  {otp}\n\n"
        f"Kode berlaku selama 5 menit.\n\n"
        f"Jika kamu tidak merasa mendaftar, abaikan email ini.\n\n"
        f"- Tim RunTrack"
    )

    try:
        with smtplib.SMTP("smtp-relay.brevo.com", 587, timeout=20) as s:
            s.ehlo()
            s.starttls(context=ssl.create_default_context())
            s.ehlo()
            s.login(brevo_user, brevo_pass)
            s.send_message(msg)
    except smtplib.SMTPAuthenticationError as exc:
        raise RuntimeError(f"Brevo SMTP Auth gagal: {exc}") from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal kirim OTP via Brevo SMTP: {exc}") from exc


def _send_via_brevo_api(api_key, sender_email, to_email, otp):
    """Brevo Transactional Email HTTP API v3.
    Daftar gratis di brevo.com > Transactional > Email > Real time > API Settings.
    Pastikan sender email sudah diverifikasi di Brevo Senders.
    """
    payload = json.dumps({
        "sender": {"name": "RunTrack", "email": sender_email},
        "to": [{"email": to_email}],
        "subject": "Kode OTP Verifikasi - RunTrack",
        "textContent": (
            f"Halo!\n\n"
            f"Kode OTP verifikasi akun RunTrack kamu adalah:\n\n"
            f"  {otp}\n\n"
            f"Kode berlaku selama 5 menit.\n\n"
            f"Jika kamu tidak merasa mendaftar, abaikan email ini.\n\n"
            f"- Tim RunTrack"
        ),
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={
            "api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status not in (200, 201):
                body = resp.read().decode()
                raise RuntimeError(f"Brevo API error {resp.status}: {body}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="ignore")
        raise RuntimeError(f"Gagal kirim OTP via Brevo API: {exc.code} {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal kirim OTP via Brevo API: {exc}") from exc
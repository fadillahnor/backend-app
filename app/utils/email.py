import os
import json
import base64
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()


def send_otp_email(to_email, otp):
    """
    Kirim OTP via HTTP API — bekerja di Railway (tidak butuh SMTP port).
    Prioritas: Mailjet → Brevo → error.

    Setup Mailjet (gratis 6000 email/bulan, aktif langsung):
      1. Daftar di app.mailjet.com
      2. Account → API Keys → copy API Key & Secret Key
      3. Tambah di Railway:
           MAILJET_API_KEY    = ...
           MAILJET_SECRET_KEY = ...
           EMAIL_USER         = emailkamu@gmail.com  (sudah ada)
    """
    mj_api_key    = os.getenv("MAILJET_API_KEY")
    mj_secret_key = os.getenv("MAILJET_SECRET_KEY")
    brevo_api_key = os.getenv("BREVO_API_KEY")
    sender_email  = os.getenv("EMAIL_USER", "noreply@runtrack.com")

    if mj_api_key and mj_secret_key:
        _send_via_mailjet(mj_api_key, mj_secret_key, sender_email, to_email, otp)
    elif brevo_api_key:
        _send_via_brevo_api(brevo_api_key, sender_email, to_email, otp)
    else:
        raise RuntimeError(
            "Gagal mengirim OTP: Set MAILJET_API_KEY + MAILJET_SECRET_KEY di Railway. "
            "Daftar gratis di app.mailjet.com."
        )


def _send_via_mailjet(api_key, secret_key, sender_email, to_email, otp):
    """Mailjet Transactional Email API v3.1
    Gratis 6000 email/bulan (200/hari). Aktif langsung setelah daftar.
    Daftar: app.mailjet.com → Account → API Keys
    Set di Railway: MAILJET_API_KEY dan MAILJET_SECRET_KEY
    """
    payload = json.dumps({
        "Messages": [
            {
                "From": {
                    "Email": sender_email,
                    "Name": "RunTrack"
                },
                "To": [
                    {
                        "Email": to_email,
                        "Name": "User"
                    }
                ],
                "Subject": "Kode OTP Verifikasi - RunTrack",
                "TextPart": (
                    f"Halo!\n\n"
                    f"Kode OTP verifikasi akun RunTrack kamu adalah:\n\n"
                    f"  {otp}\n\n"
                    f"Kode berlaku selama 5 menit.\n\n"
                    f"Jika kamu tidak merasa mendaftar, abaikan email ini.\n\n"
                    f"- Tim RunTrack"
                ),
            }
        ]
    }).encode("utf-8")

    # Basic auth: base64(api_key:secret_key)
    credentials = base64.b64encode(
        f"{api_key}:{secret_key}".encode("utf-8")
    ).decode("utf-8")

    req = urllib.request.Request(
        "https://api.mailjet.com/v3.1/send",
        data=payload,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode()
            result = json.loads(body)
            # Mailjet returns 200 even for partial failures; check Messages status
            messages = result.get("Messages", [])
            if messages and messages[0].get("Status") != "success":
                raise RuntimeError(f"Mailjet error: {messages[0]}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="ignore")
        raise RuntimeError(f"Gagal kirim OTP via Mailjet: {exc.code} {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal kirim OTP via Mailjet: {exc}") from exc


def _send_via_brevo_api(api_key, sender_email, to_email, otp):
    """Brevo Transactional Email API v3 (fallback).
    Butuh akun Brevo yang sudah diaktivasi.
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
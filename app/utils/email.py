import os
import json
import urllib.request
import urllib.error
from dotenv import load_dotenv

load_dotenv()


def send_otp_email(to_email, otp):
    brevo_key  = os.getenv("BREVO_API_KEY")
    resend_key = os.getenv("RESEND_API_KEY")
    smtp_user  = os.getenv("EMAIL_USER")

    # Prioritas 1: Brevo HTTP API — gratis 300 email/hari, tidak butuh domain,
    #              cukup verifikasi email sender di brevo.com. Bekerja di Railway.
    if brevo_key:
        sender_email = smtp_user or "noreply@runtrack.com"
        _send_via_brevo(brevo_key, sender_email, to_email, otp)

    # Prioritas 2: Resend HTTP API — butuh domain terverifikasi di resend.com/domains
    elif resend_key:
        sender_email = smtp_user or "onboarding@resend.dev"
        _send_via_resend(resend_key, sender_email, to_email, otp)

    else:
        raise RuntimeError(
            "Gagal mengirim OTP: Set BREVO_API_KEY di Railway. "
            "Daftar gratis di brevo.com (300 email/hari)."
        )


def _send_via_brevo(api_key, sender_email, to_email, otp):
    """Brevo (ex-Sendinblue) Transactional Email API v3.
    Gratis 300 email/hari. Daftar di brevo.com, verifikasi sender email,
    lalu ambil API key dari menu SMTP & API > API Keys.
    Tambahkan BREVO_API_KEY di Railway Variables.
    """
    payload = json.dumps({
        "sender": {
            "name": "RunTrack",
            "email": sender_email,
        },
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
        raise RuntimeError(f"Gagal kirim OTP via Brevo: {exc.code} {body}") from exc
    except Exception as exc:
        raise RuntimeError(f"Gagal kirim OTP via Brevo: {exc}") from exc


def _send_via_resend(api_key, sender_email, to_email, otp):
    """Resend API — butuh domain terverifikasi di resend.com/domains.
    Gunakan ini hanya jika sudah punya domain dan BREVO_API_KEY tidak ada.
    """
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
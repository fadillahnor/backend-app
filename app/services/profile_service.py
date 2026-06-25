import os
from werkzeug.utils import secure_filename
from app.models.user_model import User
from app.ext import db

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def update_profile(user_id, data, photo=None):

    user = User.query.get(user_id)

    if not user:
        return None, "User tidak ditemukan"

    user.nama = data.get("nama", user.nama)
    user.username = data.get("username", user.username)
    user.email = data.get("email", user.email)
    user.tgl_lahir = data.get("tgl_lahir", user.tgl_lahir)
    user.nohp = data.get("nohp", user.nohp)
    user.alamat = data.get("alamat", user.alamat)

    if photo:

        if not allowed_file(photo.filename):
            return None, "Format foto tidak didukung"

        # sanitize filename and ensure upload directory exists
        orig_ext = photo.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(f"user_{user.id}.{orig_ext}")

        upload_dir = os.path.join(os.getcwd(), "uploads", "profile")
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, filename)

        # save file to disk
        photo.save(filepath)

        # store path relative to project so send_from_directory can serve it
        user.foto_profile = os.path.join("uploads", "profile", filename).replace('\\', '/')

    db.session.commit()

    return user, None
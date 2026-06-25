from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from pathlib import Path

from .config import Config
from .ext import db, jwt, mail, swagger

# Load .env from backend-app root explicitly so changes are picked up
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path)

print(f"Loading environment from: {dotenv_path}")

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": "*"}})

    if app.debug:
        print("MAIL_USERNAME:", app.config.get("MAIL_USERNAME"))
        print("MAIL_PASSWORD set:", bool(app.config.get("MAIL_PASSWORD")))

    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)

    swagger.init_app(app)

    # Ensure model modules are imported so SQLAlchemy mappers are registered
    # This prevents NoReferencedTableError for foreign keys (e.g. event_categories)
    try:
        from .models import event_category_model  # noqa: F401
    except Exception:
        pass

    from .routes.auth_routes import auth_bp
    from .routes.event_routes import event_bp

    app.register_blueprint(auth_bp, url_prefix="")
    app.register_blueprint(event_bp, url_prefix="/event")

    # ================= PROFILE IMAGE =================
    @app.route('/uploads/profile/<filename>')
    def uploaded_file(filename):
        upload_folder = BASE_DIR / 'uploads' / 'profile'
        return send_from_directory(
            str(upload_folder),
            filename
        )

    @app.route('/uploads/event/<filename>')
    def event_uploaded_file(filename):
        upload_folder = BASE_DIR / 'uploads' / 'event'
        return send_from_directory(
            str(upload_folder),
            filename
        )

    return app
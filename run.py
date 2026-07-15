from app import create_app
from app.ext import db

app = create_app()

# Auto-create all tables in database on startup
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
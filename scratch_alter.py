from app import create_app
from app.ext import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE events ADD COLUMN nomor_rekening VARCHAR(100) DEFAULT NULL"))
        db.session.commit()
        print("Successfully added column: nomor_rekening")
    except Exception as e:
        print("nomor_rekening column already exists or skipped:", e)

    try:
        db.session.execute(text("ALTER TABLE events ADD COLUMN jenis_bank VARCHAR(100) DEFAULT NULL"))
        db.session.commit()
        print("Successfully added column: jenis_bank")
    except Exception as e:
        print("jenis_bank column already exists or skipped:", e)

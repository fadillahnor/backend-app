import os
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.ext import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE event_registrations ADD COLUMN scan_at DATETIME NULL;"))
            conn.commit()
            print("Successfully added scan_at column to event_registrations table!")
    except Exception as e:
        print(f"Error or column might already exist: {e}")

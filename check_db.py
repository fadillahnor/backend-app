import os
from dotenv import load_dotenv
load_dotenv()
from app import create_app
from app.ext import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('event_registrations')
    print("Columns in event_registrations:")
    for col in columns:
        print(f"- {col['name']}: {col['type']}")

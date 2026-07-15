from app import create_app
from app.ext import db
from app.models.event_category_model import EventCategory
from app.models.user_model import User
from werkzeug.security import generate_password_hash

app = create_app()

# Auto-create all tables in database on startup
with app.app_context():
    db.create_all()
    
    # Auto-seed default categories if they do not exist
    categories = [
        {"id": 1, "nama_kategori": "5K"},
        {"id": 2, "nama_kategori": "10K"},
        {"id": 3, "nama_kategori": "Half Marathon"},
        {"id": 4, "nama_kategori": "Marathon"}
    ]
    
    try:
        updated = False
        for cat_data in categories:
            existing = EventCategory.query.get(cat_data["id"])
            if not existing:
                new_cat = EventCategory(id=cat_data["id"], nama_kategori=cat_data["nama_kategori"])
                db.session.add(new_cat)
                updated = True
        if updated:
            db.session.commit()
            print("Successfully auto-seeded default categories (5K, 10K, Half Marathon, Marathon)!")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to auto-seed categories: {e}")

    # Auto-seed superadmin if it does not exist
    try:
        superadmin = User.query.filter_by(username="superadmin").first()
        if not superadmin:
            hashed_pw = generate_password_hash("superadmin123", method="pbkdf2:sha256")
            new_superadmin = User(
                nama="Super Admin",
                username="superadmin",
                password=hashed_pw,
                email="admin@runtrack.com",
                role=3,
                is_verified=True,
                nohp="08123456789",
                alamat="Kantor Super Admin"
            )
            db.session.add(new_superadmin)
            db.session.commit()
            print("Successfully auto-seeded superadmin!")
    except Exception as e:
        db.session.rollback()
        print(f"Failed to auto-seed superadmin: {e}")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
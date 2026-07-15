from app import create_app
from app.ext import db
from app.models.event_category_model import EventCategory

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

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
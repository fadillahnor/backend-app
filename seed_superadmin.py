import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.ext import db
from app.models.user_model import User
from werkzeug.security import generate_password_hash

app = create_app()

def seed_superadmin():
    email = "admin@runtrack.com"
    username = "superadmin"
    password = "superadmin123"
    
    # Generate password hash using pbkdf2:sha256 matching auth_service
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    with app.app_context():
        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            # Update password, role, and verified status
            user.email = email
            user.password = hashed_password
            user.role = 3  # SUPER_ADMIN
            user.is_verified = True
            db.session.commit()
            print(f"Super Admin dengan username '{username}' berhasil diperbarui!")
            print(f"Email: {email}")
            print(f"Password baru: {password}")
        else:
            # Create new superadmin
            superadmin = User(
                nama="Super Admin",
                username=username,
                password=hashed_password,
                email=email,
                role=3,  # 3 = SUPER_ADMIN
                is_verified=True,  # Bypass OTP verification
                nohp="08123456789",
                alamat="Kantor Super Admin"
            )
            db.session.add(superadmin)
            db.session.commit()
            print(f"Super Admin baru berhasil dibuat!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Password: {password}")

if __name__ == "__main__":
    seed_superadmin()

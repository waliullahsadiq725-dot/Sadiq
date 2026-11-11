import os
from app.database import Base, engine, SessionLocal
from app.models import User
from app.security import hash_password

Base.metadata.create_all(bind=engine)
email = os.getenv("ADMIN_EMAIL")
password = os.getenv("ADMIN_PASSWORD")
name = os.getenv("ADMIN_NAME", "NUDL Administrator")
if not email or not password:
    raise SystemExit("Set ADMIN_EMAIL and ADMIN_PASSWORD environment variables first.")
if len(password) < 8:
    raise SystemExit("ADMIN_PASSWORD must be at least 8 characters.")
db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        print("An account with this email already exists.")
    else:
        db.add(User(full_name=name, email=email.lower(), password_hash=hash_password(password), role="super_admin"))
        db.commit()
        print("Super admin account created successfully.")
finally:
    db.close()

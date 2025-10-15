"""
Run this script to populate or reset the database with default seed data.

    python -m kaihelper.domain.scripts.seed_data
"""

from sqlalchemy import inspect
from kaihelper.domain.core.database import SessionLocal, engine, Base
from kaihelper.domain.models.user import User
from passlib.hash import pbkdf2_sha256


def encrypt_password(password: str) -> str:
    """Encrypts a password using PBKDF2-SHA256."""
    return pbkdf2_sha256.hash(password)


def ensure_schema_exists():
    """Ensures all tables are created if the schema is empty."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()

    if not tables:
        print("🧱 No tables found — creating database schema...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully.")
    else:
        print(f"ℹ️  Found {len(tables)} existing tables — skipping schema creation.")


def seed_admin_user():
    """Creates or updates the default admin user."""
    db = SessionLocal()
    try:
        admin_username = "admin"
        admin_email = "admin@kaihelper.local"
        default_password = "admin"

        existing = db.query(User).filter(User.username == admin_username).first()

        if existing:
            existing.email = admin_email
            existing.full_name = "Administrator"
            existing.password = encrypt_password(default_password)
            existing.is_active = True
            db.commit()
            print("🔄 Admin user updated to default values (username='admin', password='admin').")
        else:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                full_name="Administrator",
                password=encrypt_password(default_password),
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin user created successfully (username='admin', password='admin').")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding admin user: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    ensure_schema_exists()  # ✅ Step 1: create schema if empty
    seed_admin_user()       # ✅ Step 2: seed admin user
    print("🎉 Database seeding completed.")

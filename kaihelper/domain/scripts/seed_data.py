"""
Run this script to populate or reset the database with default seed data.

Usage:
    python -m kaihelper.domain.scripts.seed_data
"""

import os
from sqlalchemy import inspect
from kaihelper.domain.core.database import SessionLocal, engine, Base
from kaihelper.domain.models.user import User
from passlib.hash import pbkdf2_sha256


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@kaihelper.local")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def encrypt_password(password: str) -> str:
    """Encrypt a password using PBKDF2-SHA256."""
    return pbkdf2_sha256.hash(password)


# ---------------------------------------------------------------------------
# Schema Setup
# ---------------------------------------------------------------------------

def ensure_schema_exists():
    """Ensures all tables are created if the schema is empty."""
    if (tables := inspect(engine).get_table_names()):
        print(f"ℹ️  Found {len(tables)} existing tables — skipping schema creation.")
    else:
        print("🧱 No tables found — creating database schema...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully.")


# ---------------------------------------------------------------------------
# Admin Seeder Helpers
# ---------------------------------------------------------------------------

def _apply_admin_defaults(user: User, db):
    """Apply default admin field values and commit the change."""
    user.email = DEFAULT_ADMIN_EMAIL
    user.full_name = "Administrator"
    user.password = encrypt_password(DEFAULT_ADMIN_PASSWORD)
    user.is_active = True
    db.commit()


def _log_admin_action(action: str):
    """Print a consistent log message for admin creation or update."""
    icons = {"create": "✅", "update": "🔄"}
    verb = "created" if action == "create" else "updated"
    print(f"{icons[action]} Admin user {verb} successfully "
          f"(username='{DEFAULT_ADMIN_USERNAME}', password='{DEFAULT_ADMIN_PASSWORD}').")


def _create_admin_user(db):
    """Create the default admin user if not existing."""
    admin_user = User(
        username=DEFAULT_ADMIN_USERNAME,
        email=DEFAULT_ADMIN_EMAIL,
        full_name="Administrator",
        password=encrypt_password(DEFAULT_ADMIN_PASSWORD),
        is_active=True,
    )
    db.add(admin_user)
    db.commit()
    _log_admin_action("create")


def _update_existing_admin(existing: User, db):
    """Update an existing admin user with default values."""
    _apply_admin_defaults(existing, db)
    _log_admin_action("update")


# ---------------------------------------------------------------------------
# Admin User Seeder
# ---------------------------------------------------------------------------

def seed_admin_user():
    """Creates or updates the default admin user."""
    with SessionLocal() as db:
        try:
            if (existing := db.query(User)
                    .filter(User.username == DEFAULT_ADMIN_USERNAME)
                    .first()):
                _update_existing_admin(existing, db)
            else:
                _create_admin_user(db)
        except Exception as e:
            db.rollback()
            print(f"❌ Error seeding admin user: {e}")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    ensure_schema_exists()   # ✅ Step 1: create schema if empty
    seed_admin_user()        # ✅ Step 2: seed admin user
    print("🎉 Database seeding completed.")
    print("⚠️  If you changed the default admin credentials, please update your environment variables accordingly.")
    print("⚠️  Do NOT use the default admin credentials in a production environment!")
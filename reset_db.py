"""
Reset the KaiHelper database (safe for MySQL).
Drops tables manually in dependency order, then recreates them.
"""

import os, sys
from sqlalchemy import text
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from kaihelper.domain.core.database import Base, engine
from kaihelper.domain.models.user import User
from kaihelper.domain.models.budget import Budget
from kaihelper.domain.models.category import Category
from kaihelper.domain.models.expense import Expense
from kaihelper.domain.models.grocery import Grocery
from kaihelper.domain.models.EmailVerificationCode import EmailVerificationCode


def reset_db():
    """Drops all tables in correct order and recreates them."""
    with engine.connect() as conn:
        print("🔧 Disabling foreign key checks...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        conn.commit()

        # --- Drop in correct dependency order ---
        drop_order = [
            "email_verification_codes",
            "groceries",
            "expenses",
            "budgets",
            "categories",
            "users"
        ]

        for table in drop_order:
            try:
                print(f"🗑️ Dropping table: {table}...")
                conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
            except Exception as e:
                print(f"⚠️ Could not drop {table}: {e}")

        conn.commit()

        print("✅ All tables dropped successfully!")

        print("🔄 Re-enabling foreign key checks...")
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        conn.commit()

    # --- Recreate tables ---
    print("🧱 Creating all tables...")
    Base.metadata.create_all(bind=engine)

    print("✅ Database reset and recreated successfully!")


if __name__ == "__main__":
    reset_db()

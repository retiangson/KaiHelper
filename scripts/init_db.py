"""
scripts/init_db.py
Initializes KaiHelper database schema using ORM.
"""

from kaihelper.core.database import init_db
from kaihelper.config.settings import settings

if __name__ == "__main__":
    print(f"Initializing ORM database using {settings.DB_ENGINE.upper()} engine...")
    init_db()
    print("ORM tables created successfully!")

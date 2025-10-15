"""
Database Configuration
Supports SQLite (default) and MySQL (via PyMySQL).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from kaihelper.config.settings import settings

if settings.DB_ENGINE == "sqlite":
    # Use file in configured dir
    db_path = os.path.join(settings.SQLITE_DIR, settings.SQLITE_FILE)
    DB_URL = f"sqlite:///{os.path.abspath(db_path)}"
else:
    # MySQL URL
    DB_URL = (
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )

engine = create_engine(DB_URL, echo=(settings.ENV == "development"), future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

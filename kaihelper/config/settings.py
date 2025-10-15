"""
config/settings.py
Centralized configuration for KaiHelper.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    # Environment
    ENV: str = os.getenv("ENV", "development")

    # Database
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite").lower()   # sqlite | mysql
    DB_NAME: str = os.getenv("DB_NAME", "kaihelper")
    DB_HOST: str = os.getenv("DB_HOST", "kaihelper-db.cfsiamsmc9v9.ap-southeast-2.rds.amazonaws.com")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "Ronfred6789")

    # Optional paths (used only when DB_ENGINE=sqlite)
    SQLITE_DIR: str = os.getenv("SQLITE_DIR", ".")
    SQLITE_FILE: str = os.getenv("SQLITE_FILE", "kaihelper.db")

    # SMTP (if/when you send emails later)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

settings = Settings()

if settings.ENV.lower() == "development":
    print(f"[KaiHelper Config] DB_ENGINE={settings.DB_ENGINE}, DB_NAME={settings.DB_NAME}, ENV={settings.ENV}")

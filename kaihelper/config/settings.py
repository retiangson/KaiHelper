"""
config/settings.py
Centralized configuration management for KaiHelper.
Loads environment variables from .env and exposes
typed settings via a dataclass for consistent access.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    # --- Database configuration ---
    DB_ENGINE: str = os.getenv("DB_ENGINE", "sqlite")           # 'sqlite' or 'mysql'
    DB_NAME: str = os.getenv("DB_NAME", "kaihelper.db")         # DB file or schema name
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # --- App secrets & environment ---
    APP_SECRET: str = os.getenv("APP_SECRET", "dev-secret-key")
    ENV: str = os.getenv("ENV", "development")

    # --- SMTP (optional email verification) ---
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "daphnie7668@gmail.com")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "L0v3UH@z3l")


# Singleton settings instance
settings = Settings()

# Optional: print summary (for debugging only)
if settings.ENV.lower() == "development":
    print(
        f"[KaiHelper Config] DB_ENGINE={settings.DB_ENGINE}, "
        f"DB_NAME={settings.DB_NAME}, ENV={settings.ENV}"
    )

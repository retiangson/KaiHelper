"""
config/settings.py
Centralized configuration for KaiHelper.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass(frozen=True)
class Settings:
    """Application-wide configuration settings loaded from environment variables."""

    # 🗄️ Database
    DB_ENGINE: str = os.getenv("DB_ENGINE", "mysql").lower()  # sqlite | mysql
    DB_NAME: str = os.getenv("DB_NAME", "kaihelper")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # 💾 Optional paths (only when using SQLite)
    SQLITE_DIR: str = os.getenv("SQLITE_DIR", ".")
    SQLITE_FILE: str = os.getenv("SQLITE_FILE", "kaihelper.db")

    # ✉️ SMTP (optional, for notifications or password recovery)
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # 🤖 OpenAI configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    USE_GPT4O: bool = os.getenv("USE_GPT4O", "true").lower() in ("1", "true", "yes")

    # 🌐 Environment
    ENV: str = os.getenv("ENV", "development")

# Instantiate a single global settings object
settings = Settings()


# 🧭 Debug log (only in development mode)
if settings.ENV.lower() == "development":
    print(
        f"[KaiHelper Config] "
        f"DB_ENGINE={settings.DB_ENGINE}, "
        f"DB_NAME={settings.DB_NAME}, "
        f"ENV={settings.ENV}, "
        f"USE_GPT4O={settings.USE_GPT4O}"
    )

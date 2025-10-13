"""
core/database.py
SQLAlchemy ORM database manager for KaiHelper.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from kaihelper.config.settings import settings

Base = declarative_base()


class DatabaseManager:
    """Singleton pattern to manage the SQLAlchemy engine and sessions."""

    _instance = None
    _engine = None
    _session_factory = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_engine(self):
        """Return (and initialize if needed) the SQLAlchemy engine."""
        if self._engine is None:
            if settings.DB_ENGINE.lower() == "mysql":
                conn_str = (
                    f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASSWORD}"
                    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
                )
            else:
                conn_str = f"sqlite:///{settings.DB_NAME}"
            self._engine = create_engine(conn_str, echo=False, future=True)
        return self._engine

    def get_session(self):
        """Return a thread-safe scoped session."""
        if self._session_factory is None:
            engine = self.get_engine()
            self._session_factory = scoped_session(sessionmaker(bind=engine))
        return self._session_factory()

    def close_session(self):
        """Close the current session."""
        if self._session_factory:
            self._session_factory.remove()


# Exported helper for Base metadata
def init_db():
    """Create all ORM tables."""
    engine = DatabaseManager().get_engine()
    Base.metadata.create_all(engine)

"""
domain/models.py
ORM entity definitions for KaiHelper using SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from kaihelper.core.database import Base
from dataclasses import dataclass


class User(Base):
    """User ORM entity representing system users."""

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    provider = Column(String(50), default="local")
    email_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class EmailVerificationCode(Base):
    """Email verification codes linked to users."""

    __tablename__ = "email_verification_codes"

    code_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    code = Column(String(10), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)


# ----------------- DTOs (Data Transfer Objects) -----------------

@dataclass
class UserDTO:
    """Lightweight DTO for user data transfer across layers."""
    user_id: int
    name: str
    email: str
    email_verified: bool


@dataclass
class RegisterUserDTO:
    """DTO for user registration input."""
    name: str
    email: str
    password: str

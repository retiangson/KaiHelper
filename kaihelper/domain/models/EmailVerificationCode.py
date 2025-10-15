"""
domain/models/EmailVerificationCode.py
ORM entity definitions for KaiHelper using SQLAlchemy.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from kaihelper.domain.core.database import Base
from dataclasses import dataclass

class EmailVerificationCode(Base):
    """Email verification codes linked to users."""

    __tablename__ = "email_verification_codes"

    code_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))  # ✅ Fixed reference
    code = Column(String(10), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

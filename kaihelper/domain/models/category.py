from sqlalchemy import Column, Integer, String, DateTime, func
from kaihelper.domain.core.database import Base

class Category(Base):
    """Represents a grocery category."""
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

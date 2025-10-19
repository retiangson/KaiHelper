from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import relationship
from kaihelper.domain.core.database import Base

class Grocery(Base):
    """Represents a grocery item purchased by a user."""
    __tablename__ = "groceries"

    grocery_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    expense_id = Column(Integer, ForeignKey("expenses.expense_id"), nullable=True)
    
    item_name = Column(String(100), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    purchase_date = Column(Date, nullable=False)
    notes = Column(String(255))
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    receipt_image = Column(String(255), nullable=True)
    total_cost = Column(Float, nullable=False)
    local = Column(Boolean, nullable=True, default=None)

    expense = relationship("Expense", back_populates="groceries")
    

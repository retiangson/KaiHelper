from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from kaihelper.domain.core.database import Base

class Expense(Base):
    """Represents an expense entry."""
    __tablename__ = "expenses"

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    grocery_id = Column(Integer, ForeignKey("groceries.grocery_id"), nullable=True)
    amount = Column(Float, nullable=False)
    description = Column(String(255))
    expense_date = Column(Date, nullable=False)
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=False)
    receipt_image = Column(String(255))  # URL or path to the receipt image
    notes = Column(String(500))  # Additional notes about the expense
    
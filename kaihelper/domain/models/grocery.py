from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from kaihelper.domain.core.database import Base

class Grocery(Base):
    """Represents a grocery item purchased by a user."""
    __tablename__ = "groceries"

    grocery_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    item_name = Column(String(100), nullable=False)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    purchase_date = Column(Date, nullable=False)
    notes = Column(String(255))
    created_at = Column(Date, nullable=False)
    updated_at = Column(Date, nullable=True)
    receipt_image = Column(String(255), nullable=True)  # URL or path to the receipt image
    total_cost = Column(Float, nullable=False)  # Computed as unit_price * quantity
    

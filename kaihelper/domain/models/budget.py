from sqlalchemy import Column, Integer, Float, ForeignKey, Date
from kaihelper.domain.core.database import Base

class Budget(Base):
    """Represents a user's budget period."""
    __tablename__ = "budgets"

    budget_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_budget = Column(Float, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    remaining_balance = Column(Float, nullable=False)

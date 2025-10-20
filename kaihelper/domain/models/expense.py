"""
Expense ORM Model
Represents a user's expense entry with extended metadata
for receipt tracking and analytics.
"""

# --- Third-party imports ---
from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
# --- First-party imports ---
from kaihelper.domain.core.database import Base


class Expense(Base):
    """
    Represents an expense entry, optionally linked to a grocery record
    or created from an uploaded receipt.

    Attributes:
        expense_id (int): Primary key.
        user_id (int): Reference to the user who owns this expense.
        category_id (int): Linked category (e.g., Groceries, Bills).
        grocery_id (int | None): Optional link to a grocery item.
        amount (float): Expense amount.
        description (str): Description of the expense.
        expense_date (date): Date when the expense occurred.
        created_at (date): Record creation timestamp.
        updated_at (date): Record last update timestamp.
        receipt_image (str | None): Path or URL to the receipt image.
        notes (str | None): Additional user notes about the expense.

        # New fields:
        store_name (str | None): Name of the store or merchant.
        store_address (str | None): Address or location of the merchant.
        receipt_number (str | None): Identifier printed on the receipt.
        payment_method (str | None): Payment method (Cash, Card, etc.).
        currency (str | None): Currency code (e.g., NZD, USD).
        subtotal_amount (float | None): Pre-tax subtotal.
        tax_amount (float | None): Tax portion of the expense.
        discount_amount (float | None): Discount applied to the total.
        due_date (date | None): Optional due date for bill-type receipts.
        suggestion (str | None): AI-provided suggestion for categorization.
    """

    __tablename__ = "expenses"

    # --- Core fields ---
    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(255), nullable=True)
    expense_date = Column(Date, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    receipt_image = Column(String(255), nullable=True)
    notes = Column(String(500), nullable=True)

    # --- Extended metadata fields (nullable for flexibility) ---
    store_name = Column(String(150), nullable=True)
    store_address = Column(String(255), nullable=True)
    receipt_number = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=True)
    currency = Column(String(10), nullable=True)
    subtotal_amount = Column(Float, nullable=True)
    tax_amount = Column(Float, nullable=True)
    discount_amount = Column(Float, nullable=True)
    due_date = Column(Date, nullable=True)
    suggestion = Column(String(255), nullable=True)

    # --- Relationships ---
    category = relationship("Category", back_populates="expenses", lazy="joined")
    groceries = relationship("Grocery", back_populates="expense", lazy="joined")
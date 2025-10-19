"""
GroceryDTO
Data Transfer Object representing grocery item details for budgeting and receipt tracking.
"""

# --- Standard library imports ---
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class GroceryDTO:
    """
    Represents a grocery record associated with a user’s expenses.

    Attributes:
        grocery_id (int | None): Unique identifier for the grocery record.
        user_id (int): Identifier of the user who owns this grocery item.
        category_id (int | None): Optional category ID (e.g., Groceries, Supplies).
        item_name (str): Name of the grocery item.
        unit_price (float): Price per item or unit.
        quantity (float): Quantity purchased (supports fractional values).
        purchase_date (date): Date when the item was purchased.
        notes (str | None): Optional notes, e.g., auto-generated or manual remarks.
        created_at (date | None): Timestamp when the record was created.
        updated_at (date | None): Timestamp when the record was last updated.
        receipt_image (str | None): Optional URL or path to a related receipt image.
        total_cost (float | None): Computed total cost (unit_price × quantity).
    """
    grocery_id: Optional[int] = None
    user_id: int = 0
    category_id: Optional[int] = None
    expense_id: Optional[int] = None
    item_name: str = ""
    unit_price: float = 0.0
    quantity: float = 1.0
    purchase_date: date = date.today()
    notes: Optional[str] = None
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    receipt_image: Optional[str] = None
    total_cost: Optional[float] = None
    local: Optional[bool] = None

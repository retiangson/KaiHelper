"""
ExpenseDTO
Data Transfer Object representing an expense entry for API and business layers.
"""

# --- Standard library imports ---
from dataclasses import dataclass
from datetime import date


@dataclass
class ExpenseDTO:
    """
    Represents a user expense record including amount, category, and related metadata.

    Attributes:
        expense_id (int | None): Unique identifier for the expense.
        user_id (int): Identifier of the user who owns the expense.
        category_id (int): Identifier of the associated category.
        grocery_id (int | None): Optional link to a grocery record.
        amount (float): Expense amount in the user’s preferred currency.
        description (str | None): Optional short description of the expense.
        expense_date (date): Date when the expense occurred.
        created_at (date | None): Timestamp when the expense was created.
        updated_at (date | None): Timestamp when the expense was last updated.
        receipt_image (str | None): Optional URL or file path to the receipt image.
        notes (str | None): Additional notes or comments about the expense.
    """
    expense_id: int | None = None
    user_id: int = 0
    category_id: int = 0
    grocery_id: int | None = None
    amount: float = 0.0
    description: str | None = None
    expense_date: date | None = None
    created_at: date | None = None
    updated_at: date | None = None
    receipt_image: str | None = None
    notes: str | None = None

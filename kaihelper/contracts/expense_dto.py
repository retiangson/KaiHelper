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
    Represents a user expense record including amount, category, and detailed receipt metadata.

    Attributes:
        expense_id (int | None): Unique identifier for the expense.
        user_id (int): Identifier of the user who owns the expense.
        category_id (int): Identifier of the associated category.
        grocery_id (int | None): Optional link to a grocery record.
        amount (float): Expense amount in the user’s preferred currency.
        description (str | None): Optional short description of the expense.
        expense_date (date | None): Date when the expense occurred.
        created_at (date | None): Timestamp when the expense was created.
        updated_at (date | None): Timestamp when the expense was last updated.
        receipt_image (str | None): Optional URL or file path to the receipt image.
        notes (str | None): Additional notes or comments about the expense.

        store_name (str | None): Name of the store or merchant.
        store_address (str | None): Address or location of the merchant.
        receipt_number (str | None): Receipt or invoice number.
        payment_method (str | None): Payment type (e.g., Cash, Card, Online).
        currency (str | None): Currency code (e.g., NZD, USD).
        subtotal_amount (float | None): Pre-tax subtotal amount.
        tax_amount (float | None): Tax portion of the total.
        discount_amount (float | None): Discount applied to the total.
        due_date (date | None): Optional due date (for bill/invoice expenses).
        suggestion (str | None): AI-provided categorization or budgeting hint.
    """
    expense_id: int | None = None
    user_id: int = 0
    category_id: int = 0
    amount: float = 0.0
    description: str | None = None
    expense_date: date | None = None
    created_at: date | None = None
    updated_at: date | None = None
    receipt_image: str | None = None
    notes: str | None = None

    # --- Extended metadata fields ---
    store_name: str | None = None
    store_address: str | None = None
    receipt_number: str | None = None
    payment_method: str | None = None
    currency: str | None = None
    subtotal_amount: float | None = None
    tax_amount: float | None = None
    discount_amount: float | None = None
    due_date: date | None = None
    suggestion: str | None = None
    category_name: str | None = None
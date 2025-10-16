from dataclasses import dataclass
from datetime import date

@dataclass
class ExpenseDTO:
    expense_id: int | None
    user_id: int
    category_id: int
    grocery_id: int | None
    amount: float
    description: str | None
    expense_date: date
    created_at: date | None = None
    updated_at: date | None = None
    receipt_image: str | None = None  # URL or path to the receipt image
    notes: str | None = None  # Additional notes about the expense
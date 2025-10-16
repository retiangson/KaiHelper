"""
BudgetDTO
Data Transfer Object for budget information exchanged between layers.
"""

# --- Standard library imports ---
from dataclasses import dataclass
from datetime import date


@dataclass
class BudgetDTO:
    """
    Represents a user's budget details, including total, duration, and remaining balance.

    Attributes:
        budget_id (int | None): Unique identifier for the budget record.
        user_id (int): Associated user ID.
        total_budget (float): The total allocated budget amount.
        start_date (date): The start date of the budget period.
        end_date (date): The end date of the budget period.
        remaining_balance (float): Remaining amount in the budget.
    """
    budget_id: int | None = None
    user_id: int = 0
    total_budget: float = 0.0
    start_date: date | None = None
    end_date: date | None = None
    remaining_balance: float = 0.0

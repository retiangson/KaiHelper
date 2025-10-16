from dataclasses import dataclass
from datetime import date

@dataclass
class BudgetDTO:
    budget_id: int | None
    user_id: int
    total_budget: float
    start_date: date
    end_date: date
    remaining_balance: float
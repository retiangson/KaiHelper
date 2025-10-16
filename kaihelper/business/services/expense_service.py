"""
ExpenseService
Implements business logic for Expense operations with budget synchronization.
"""

from datetime import date, datetime
from kaihelper.business.interfaces.iexpense_service import IExpenseService
from kaihelper.domain.repositories.expense_repository import ExpenseRepository
from kaihelper.domain.repositories.budget_repository import BudgetRepository
from kaihelper.contracts.expense_dto import ExpenseDTO
from kaihelper.contracts.result_dto import ResultDTO


class ExpenseService(IExpenseService):
    """Implements business logic for Expense operations."""

    def __init__(self, repository: ExpenseRepository | None = None):
        self._expense_repo = repository or ExpenseRepository()
        self._budget_repo = BudgetRepository()

    # ------------------------------------------------------------------
    def add_expense(self, dto: ExpenseDTO) -> ResultDTO:
        """
        Add a new expense and update user's active budget.
        """
        # 🧩 Validation
        if dto.amount <= 0:
            return ResultDTO(False, "Expense amount must be greater than zero.")
        if not dto.user_id:
            return ResultDTO(False, "User ID is required.")
        if not dto.expense_date or dto.expense_date > date.today():
            return ResultDTO(False, "Invalid expense date.")

        # 🧾 Create the expense
        result = self._expense_repo.create(dto)
        if not result.success:
            return result

        # 🧮 Deduct from user's active budget (if any)
        active_budgets = self._budget_repo.get_active_budgets(dto.user_id)
        if not active_budgets.success or not active_budgets.data:
            return ResultDTO(True, "Expense recorded, but no active budget found.", result.data)

        latest_budget = active_budgets.data[-1]
        if latest_budget.start_date <= dto.expense_date <= latest_budget.end_date:
            remaining = latest_budget.remaining_balance - dto.amount
            if remaining < 0:
                return ResultDTO(False, "Insufficient budget balance.")
            latest_budget.remaining_balance = remaining
            self._budget_repo.update(latest_budget)  # ✅ changed to update instead of create

        return ResultDTO(True, "Expense added and budget updated.", result.data)

    # ------------------------------------------------------------------
    def update_expense(self, dto: ExpenseDTO) -> ResultDTO:
        """
        Update an existing expense record.
        Adjusts the budget difference if amount changes.
        """
        if not dto.expense_id:
            return ResultDTO(False, "Expense ID is required for update.")

        existing = self._expense_repo.get_by_id(dto.expense_id)
        if not existing.success or not existing.data:
            return ResultDTO(False, "Expense not found.")

        old_expense = existing.data
        difference = dto.amount - old_expense.amount

        # 🧾 Update expense
        result = self._expense_repo.update(dto)
        if not result.success:
            return result

        # 🧮 Adjust active budget (if affected)
        active_budgets = self._budget_repo.get_active_budgets(dto.user_id)
        if active_budgets.success and active_budgets.data:
            latest_budget = active_budgets.data[-1]
            if latest_budget.start_date <= dto.expense_date <= latest_budget.end_date:
                latest_budget.remaining_balance -= difference
                self._budget_repo.update(latest_budget)

        return ResultDTO(True, "Expense updated successfully.", result.data)

    # ------------------------------------------------------------------
    def list_expenses(self, user_id: int) -> ResultDTO:
        """List all expenses for a given user."""
        if not user_id:
            return ResultDTO(False, "User ID is required.")
        return self._expense_repo.get_all(user_id)

    # ------------------------------------------------------------------
    def find_by_grocery_id(self, grocery_id: int) -> ResultDTO:
        """
        Find an expense linked to a specific grocery.
        Used by ReceiptService to sync grocery-based expenses.
        """
        try:
            result = self._expense_repo.get_by_grocery_id(grocery_id)
            if result and result.success and result.data:
                return ResultDTO.ok("Expense found", result.data)
            return ResultDTO.error("Expense not found")
        except Exception as e:
            return ResultDTO.error(f"Failed to find expense by grocery ID: {e}")

    # ------------------------------------------------------------------
    def get_expense_by_id(self, expense_id: int) -> ResultDTO:
        """Retrieve an expense record by its ID."""
        if not expense_id:
            return ResultDTO(False, "Expense ID is required.")
        return self._expense_repo.get_by_id(expense_id)

    # ------------------------------------------------------------------
    def delete_expense(self, expense_id: int) -> ResultDTO:
        """
        Delete an expense and optionally adjust budget balance.
        """
        try:
            existing = self._expense_repo.get_by_id(expense_id)
            if not existing.success or not existing.data:
                return ResultDTO(False, "Expense not found.")

            expense = existing.data

            # 💰 Restore amount to active budget
            active_budgets = self._budget_repo.get_active_budgets(expense.user_id)
            if active_budgets.success and active_budgets.data:
                latest_budget = active_budgets.data[-1]
                if latest_budget.start_date <= expense.expense_date <= latest_budget.end_date:
                    latest_budget.remaining_balance += expense.amount
                    self._budget_repo.update(latest_budget)

            # 🗑️ Delete expense
            result = self._expense_repo.delete(expense_id)
            if not result.success:
                return ResultDTO.error(result.message)

            return ResultDTO.ok("Expense deleted and budget restored.", result.data)
        except Exception as e:
            return ResultDTO.error(f"Failed to delete expense: {e}")

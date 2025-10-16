"""
ExpenseService
Implements business logic for Expense operations with budget synchronization.
"""

# --- Standard library imports ---
from datetime import date

# --- First-party imports ---
from kaihelper.business.interfaces.iexpense_service import IExpenseService
from kaihelper.domain.repositories.expense_repository import ExpenseRepository
from kaihelper.domain.repositories.budget_repository import BudgetRepository
from kaihelper.contracts.expense_dto import ExpenseDTO
from kaihelper.contracts.result_dto import ResultDTO


class ExpenseService(IExpenseService):
    """Implements business logic for Expense operations."""

    def __init__(self, repository: ExpenseRepository | None = None) -> None:
        """
        Initialize the ExpenseService.

        Args:
            repository (ExpenseRepository | None): Optional repository for dependency injection.
        """
        self._expense_repo = repository or ExpenseRepository()
        self._budget_repo = BudgetRepository()

    def add_expense(self, dto: ExpenseDTO) -> ResultDTO:
        """
        Add a new expense and update the user's active budget.

        Args:
            dto (ExpenseDTO): Expense data transfer object.

        Returns:
            ResultDTO: Result of the operation.
        """
        if dto.amount <= 0:
            return ResultDTO(False, "Expense amount must be greater than zero.")
        if not dto.user_id:
            return ResultDTO(False, "User ID is required.")
        if not dto.expense_date or dto.expense_date > date.today():
            return ResultDTO(False, "Invalid expense date.")

        result = self._expense_repo.create(dto)
        if not result.success:
            return result

        active_budgets = self._budget_repo.get_active_budgets(dto.user_id)
        if not active_budgets.success or not active_budgets.data:
            return ResultDTO(True, "Expense recorded, but no active budget found.", result.data)

        latest_budget = active_budgets.data[-1]
        if latest_budget.start_date <= dto.expense_date <= latest_budget.end_date:
            remaining = latest_budget.remaining_balance - dto.amount
            if remaining < 0:
                return ResultDTO(False, "Insufficient budget balance.")
            latest_budget.remaining_balance = remaining
            self._budget_repo.update(latest_budget)

        return ResultDTO(True, "Expense added and budget updated.", result.data)

    def update_expense(self, dto: ExpenseDTO) -> ResultDTO:
        """
        Update an existing expense record and adjust the active budget if necessary.

        Args:
            dto (ExpenseDTO): Updated expense data.

        Returns:
            ResultDTO: Operation result.
        """
        if not dto.expense_id:
            return ResultDTO(False, "Expense ID is required for update.")

        existing = self._expense_repo.get_by_id(dto.expense_id)
        if not existing.success or not existing.data:
            return ResultDTO(False, "Expense not found.")

        old_expense = existing.data
        difference = dto.amount - old_expense.amount

        result = self._expense_repo.update(dto)
        if not result.success:
            return result

        active_budgets = self._budget_repo.get_active_budgets(dto.user_id)
        if active_budgets.success and active_budgets.data:
            latest_budget = active_budgets.data[-1]
            if latest_budget.start_date <= dto.expense_date <= latest_budget.end_date:
                latest_budget.remaining_balance -= difference
                self._budget_repo.update(latest_budget)

        return ResultDTO(True, "Expense updated successfully.", result.data)

    def list_expenses(self, user_id: int) -> ResultDTO:
        """
        Retrieve all expenses for a specific user.

        Args:
            user_id (int): User identifier.

        Returns:
            ResultDTO: Operation result with list of expenses.
        """
        if not user_id:
            return ResultDTO(False, "User ID is required.")
        return self._expense_repo.get_all(user_id)

    def find_by_grocery_id(self, grocery_id: int) -> ResultDTO:
        """
        Retrieve an expense linked to a specific grocery record.

        Args:
            grocery_id (int): Grocery identifier.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            result = self._expense_repo.get_by_grocery_id(grocery_id)
            if result and result.success and result.data:
                return ResultDTO.ok("Expense found", result.data)
            return ResultDTO.fail("Expense not found")
        except Exception as err:
            return ResultDTO.fail(f"Failed to find expense by grocery ID: {repr(err)}")

    def get_expense_by_id(self, expense_id: int) -> ResultDTO:
        """
        Retrieve an expense record by its unique identifier.

        Args:
            expense_id (int): Expense identifier.

        Returns:
            ResultDTO: Operation result.
        """
        if not expense_id:
            return ResultDTO(False, "Expense ID is required.")
        return self._expense_repo.get_by_id(expense_id)

    def delete_expense(self, expense_id: int) -> ResultDTO:
        """
        Delete an expense and adjust the budget if applicable.

        Args:
            expense_id (int): Expense identifier.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            existing = self._expense_repo.get_by_id(expense_id)
            if not existing.success or not existing.data:
                return ResultDTO(False, "Expense not found.")

            expense = existing.data

            active_budgets = self._budget_repo.get_active_budgets(expense.user_id)
            if active_budgets.success and active_budgets.data:
                latest_budget = active_budgets.data[-1]
                if latest_budget.start_date <= expense.expense_date <= latest_budget.end_date:
                    latest_budget.remaining_balance += expense.amount
                    self._budget_repo.update(latest_budget)

            result = self._expense_repo.delete(expense_id)
            if not result.success:
                return ResultDTO.fail(result.message)

            return ResultDTO.ok("Expense deleted and budget restored.", result.data)
        except Exception as err:
            return ResultDTO.fail(f"Failed to delete expense: {repr(err)}")

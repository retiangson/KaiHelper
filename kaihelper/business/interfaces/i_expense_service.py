from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.expense_dto import ExpenseDTO
from datetime import date


class IExpenseService(ABC):
    """Interface for expense business logic."""

    @abstractmethod
    def add_expense(self, dto: ExpenseDTO) -> ResultDTO:
        """Add a new expense record and update active budget."""
        pass

    @abstractmethod
    def update_expense(self, dto: ExpenseDTO) -> ResultDTO:
        """Update an existing expense and adjust budget differences."""
        pass

    @abstractmethod
    def list_expenses(self, user_id: int) -> ResultDTO:
        """List all expenses for a specific user."""
        pass

    @abstractmethod
    def find_by_grocery_id(self, grocery_id: int) -> ResultDTO:
        """Find an expense linked to a specific grocery (used by ReceiptService)."""
        pass

    @abstractmethod
    def get_expense_by_id(self, expense_id: int) -> ResultDTO:
        """Retrieve an expense record by its ID."""
        pass

    @abstractmethod
    def delete_expense(self, expense_id: int) -> ResultDTO:
        """Delete an expense and restore its amount to the active budget."""
        pass

    @abstractmethod
    def check_exist(self, user_id: int, store_name: str, expense_date: date) -> ResultDTO:
        """Check if an expense exists for a user by store name and expense date."""
        pass

from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.expense_dto import ExpenseDTO


class IExpenseRepository(ABC):
    """Interface for expense repository operations."""

    @abstractmethod
    def create(self, dto: ExpenseDTO) -> ResultDTO:
        """Create a new expense record."""
        pass

    @abstractmethod
    def update(self, dto: ExpenseDTO) -> ResultDTO:
        """Update an existing expense record."""
        pass

    @abstractmethod
    def get_all(self, user_id: int) -> ResultDTO:
        """Retrieve all expenses for a specific user."""
        pass

    @abstractmethod
    def get_by_id(self, expense_id: int) -> ResultDTO:
        """Retrieve an expense by its ID."""
        pass

    @abstractmethod
    def get_by_grocery_id(self, grocery_id: int) -> ResultDTO:
        """Retrieve an expense associated with a specific grocery record."""
        pass

    @abstractmethod
    def delete(self, expense_id: int) -> ResultDTO:
        """Delete an expense record by ID."""
        pass

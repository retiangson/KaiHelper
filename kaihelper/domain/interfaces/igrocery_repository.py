from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.grocery_dto import GroceryDTO


class IGroceryRepository(ABC):
    """Interface for grocery repository operations."""

    @abstractmethod
    def create(self, dto: GroceryDTO) -> ResultDTO:
        """Create a new grocery record."""
        pass

    @abstractmethod
    def get_all(self, user_id: int) -> ResultDTO:
        """Retrieve all groceries for a specific user."""
        pass

    @abstractmethod
    def get_by_id(self, grocery_id: int) -> ResultDTO:
        """Retrieve a grocery record by its ID."""
        pass

    @abstractmethod
    def get_by_name(self, user_id: int, item_name: str) -> ResultDTO:
        """Retrieve a grocery record by its item name for a specific user."""
        pass

    @abstractmethod
    def update(self, dto: GroceryDTO) -> ResultDTO:
        """Update an existing grocery record."""
        pass

    @abstractmethod
    def delete(self, grocery_id: int) -> ResultDTO:
        """Delete a grocery record by ID."""
        pass

    @abstractmethod
    def get_by_expense_id(self, expense_id: int) -> ResultDTO:
        """Retrieve a grocery record associated with a specific expense ID."""
        pass

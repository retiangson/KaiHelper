from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.grocery_dto import GroceryDTO


class IGroceryService(ABC):
    """Interface for grocery business logic."""

    @abstractmethod
    def add_grocery(self, dto: GroceryDTO) -> ResultDTO:
        """Add a new grocery record."""
        pass

    @abstractmethod
    def list_groceries(self, user_id: int) -> ResultDTO:
        """List all groceries for a specific user."""
        pass

    @abstractmethod
    def find_by_name(self, user_id: int, item_name: str) -> ResultDTO:
        """Find an existing grocery by item name for a specific user."""
        pass

    @abstractmethod
    def update_grocery(self, dto: GroceryDTO) -> ResultDTO:
        """Update an existing grocery record."""
        pass

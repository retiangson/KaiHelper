from kaihelper.business.interfaces.igrocery_service import IGroceryService
from kaihelper.domain.repositories.grocery_repository import GroceryRepository
from kaihelper.contracts.grocery_dto import GroceryDTO
from kaihelper.contracts.result_dto import ResultDTO


class GroceryService(IGroceryService):
    """Implements business logic for Grocery operations."""

    def __init__(self, repository: GroceryRepository | None = None):
        """Allow optional dependency injection."""
        self._repo = repository or GroceryRepository()

    # ------------------------------------------------------------------
    def add_grocery(self, dto: GroceryDTO) -> ResultDTO:
        """Add a new grocery record."""
        if not dto.item_name or dto.unit_price <= 0 or dto.quantity <= 0:
            return ResultDTO(False, "Invalid grocery details. Please check name, price, and quantity.")
        return self._repo.create(dto)

    # ------------------------------------------------------------------
    def list_groceries(self, user_id: int) -> ResultDTO:
        """Return all groceries for a user."""
        if not user_id:
            return ResultDTO(False, "User ID is required.")
        return self._repo.get_all(user_id)

    # ------------------------------------------------------------------
    def find_by_name(self, user_id: int, item_name: str) -> ResultDTO:
        """
        Find a grocery item by name for a specific user.
        Used in ReceiptService to prevent duplicate entries.
        """
        try:
            result = self._repo.get_by_name(user_id, item_name)
            if result and result.success and result.data:
                return ResultDTO.ok("Grocery found", result.data)
            return ResultDTO.error("Grocery not found")
        except Exception as e:
            return ResultDTO.error(f"Failed to find grocery by name: {e}")

    # ------------------------------------------------------------------
    def update_grocery(self, dto: GroceryDTO) -> ResultDTO:
        """
        Update an existing grocery record.
        Ensures grocery_id is provided before updating.
        """
        try:
            if not dto.grocery_id:
                return ResultDTO.error("Grocery ID is required for update.")
            if dto.unit_price <= 0 or dto.quantity <= 0:
                return ResultDTO.error("Invalid grocery details for update.")

            result = self._repo.update(dto)
            if result and result.success:
                return ResultDTO.ok("Grocery updated successfully", result.data)
            return ResultDTO.error(result.message if result else "Failed to update grocery")
        except Exception as e:
            return ResultDTO.error(f"Error updating grocery: {e}")

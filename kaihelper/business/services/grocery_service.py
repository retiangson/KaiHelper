"""
GroceryService
Implements business logic for Grocery operations.
"""

# --- First-party imports ---
from kaihelper.business.interfaces.igrocery_service import IGroceryService
from kaihelper.domain.repositories.grocery_repository import GroceryRepository
from kaihelper.contracts.grocery_dto import GroceryDTO
from kaihelper.contracts.result_dto import ResultDTO


class GroceryService(IGroceryService):
    """Service layer implementing business logic for grocery operations."""

    def __init__(self, repository: GroceryRepository | None = None) -> None:
        """
        Initialize the GroceryService with an optional repository.

        Args:
            repository (GroceryRepository | None): Optional repository for dependency injection.
        """
        self._repo = repository or GroceryRepository()

    def add_grocery(self, dto: GroceryDTO) -> ResultDTO:
        """
        Add a new grocery record after validation.

        Args:
            dto (GroceryDTO): Grocery data transfer object.

        Returns:
            ResultDTO: Operation result.
        """
        if not dto.item_name or not isinstance(dto.quantity, (int, float)) or dto.unit_price <= 0 or dto.quantity <= 0:
            return ResultDTO.fail(
                "Invalid grocery details. Please check name, price, and quantity."
            )
        return self._repo.create(dto)

    def list_groceries(self, user_id: int) -> ResultDTO:
        """
        Retrieve all groceries for a user.

        Args:
            user_id (int): User identifier.

        Returns:
            ResultDTO: Operation result with grocery list.
        """
        if not user_id:
            return ResultDTO.fail("User ID is required.")
        return self._repo.get_all(user_id)

    def find_by_name(self, user_id: int, item_name: str) -> ResultDTO:
        """
        Retrieve a grocery item by name for a specific user.

        Args:
            user_id (int): User identifier.
            item_name (str): Grocery item name.

        Returns:
            ResultDTO: Operation result with grocery data or error.
        """
        try:
            result = self._repo.get_by_name(user_id, item_name)
            if result and result.success and result.data:
                return ResultDTO.ok("Grocery found", result.data)
            return ResultDTO.fail("Grocery not found")
        except Exception as err:  # pylint: disable=broad-except
            return ResultDTO.fail(f"Failed to find grocery by name: {repr(err)}")

    def update_grocery(self, dto: GroceryDTO) -> ResultDTO:
        """
        Update an existing grocery record after validating the input.

        Args:
            dto (GroceryDTO): Updated grocery data transfer object.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            if not dto.grocery_id:
                return ResultDTO.fail("Grocery ID is required for update.")
            if dto.unit_price <= 0 or dto.quantity <= 0:
                return ResultDTO.fail("Invalid grocery details for update.")

            result = self._repo.update(dto)
            if result and result.success:
                return ResultDTO.ok("Grocery updated successfully", result.data)
            return ResultDTO.fail(result.message if result else "Failed to update grocery")
        except Exception as err:  # pylint: disable=broad-except
            return ResultDTO.fail(f"Error updating grocery: {repr(err)}")

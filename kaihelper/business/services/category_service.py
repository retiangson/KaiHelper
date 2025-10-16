"""
CategoryService
Handles category business logic.
"""

# --- First-party imports ---
from kaihelper.business.interfaces.icategory_service import ICategoryService
from kaihelper.domain.repositories.category_repository import CategoryRepository
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.category_dto import CategoryDTO


class CategoryService(ICategoryService):
    """Service layer for managing category operations."""

    def __init__(self, repository: CategoryRepository | None = None) -> None:
        """
        Initialize the CategoryService with an optional repository.

        Args:
            repository (CategoryRepository | None): Optional injected repository for dependency testing.
        """
        self._repo = repository or CategoryRepository()

    def list_categories(self) -> ResultDTO:
        """
        Retrieve all available categories.

        Returns:
            ResultDTO: List of categories or error message.
        """
        try:
            categories = self._repo.get_all()
            return ResultDTO.success("Categories retrieved successfully", categories)
        except Exception as err:
            return ResultDTO.error(f"Failed to retrieve categories: {repr(err)}")

    def add_category(self, dto: CategoryDTO) -> ResultDTO:
        """
        Add a new category.

        Args:
            dto (CategoryDTO): Data transfer object containing category details.

        Returns:
            ResultDTO: Operation result with success or failure message.
        """
        try:
            result = self._repo.create(dto)
            if result.success:
                return ResultDTO.success("Category added successfully", result.data)
            return ResultDTO.error(result.message)
        except Exception as err:
            return ResultDTO.error(f"Failed to add category: {repr(err)}")

    def delete_category(self, category_id: int) -> ResultDTO:
        """
        Delete a category by ID.

        Args:
            category_id (int): Unique identifier of the category.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            result = self._repo.delete(category_id)
            if result.success:
                return ResultDTO.success("Category deleted successfully")
            return ResultDTO.error(result.message)
        except Exception as err:
            return ResultDTO.error(f"Failed to delete category: {repr(err)}")

    def get_category(self, category_name: str) -> ResultDTO:
        """
        Retrieve a category by its name.

        Args:
            category_name (str): Name of the category.

        Returns:
            ResultDTO: Operation result with the category or error message.
        """
        try:
            category = self._repo.get_by_name(category_name)
            if category.success:
                return ResultDTO.success("Category retrieved successfully", category.data)
            return ResultDTO.error("Category not found")
        except Exception as err:
            return ResultDTO.error(f"Failed to retrieve category: {repr(err)}")

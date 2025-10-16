"""
CategoryService
Handles category business logic.
"""
from kaihelper.domain.repositories.category_repository import CategoryRepository
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.category_dto import CategoryDTO
from kaihelper.business.interfaces.icategory_service import ICategoryService


class CategoryService(ICategoryService):
    """Service layer for category operations."""

    def __init__(self, repository: CategoryRepository | None = None):
        self._repo = repository or CategoryRepository()

    def list_categories(self) -> ResultDTO:
        try:
            categories = self._repo.get_all()
            return ResultDTO.ok("Categories retrieved successfully", categories)
        except Exception as e:
            return ResultDTO.fail(f"Failed to retrieve categories: {e}")

    def add_category(self, dto: CategoryDTO) -> ResultDTO:
        try:
            result = self._repo.create(dto)
            if result.success:
                return ResultDTO.ok("Category added successfully", result.data)
            return ResultDTO.error(result.message)
        
        except Exception as e:
            return ResultDTO.fail(f"Failed to add category: {e}")

    def delete_category(self, category_id: int) -> ResultDTO:
        try:
            result = self._repo.delete(category_id)
            if result.success:
                return ResultDTO.ok("Category deleted successfully")
            return ResultDTO.fail(result.message)
        except Exception as e:
            return ResultDTO.fail(f"Failed to delete category: {e}")
        
    def get_category(self, category_name: str) -> ResultDTO:
        try:
            category = self._repo.get_by_name(category_name)
            if category.success:
                return ResultDTO.ok("Category retrieved successfully", category.data)
            return ResultDTO.fail("Category not found")
        except Exception as e:
            return ResultDTO.fail(f"Failed to retrieve category: {e}")
    

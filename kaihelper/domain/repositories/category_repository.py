"""
CategoryRepository
Handles database persistence and CRUD operations for Category entities.
"""

# --- Standard library imports ---
# (none)

# --- Third-party imports ---
from sqlalchemy.exc import SQLAlchemyError

# --- First-party imports ---
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.category import Category
from kaihelper.domain.mappers.category_mapper import CategoryMapper
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.category_dto import CategoryDTO


class CategoryRepository:
    """Repository for CRUD operations on Category entities."""

    def create(self, dto: CategoryDTO) -> ResultDTO:
        """
        Create a new category.

        Args:
            dto (CategoryDTO): Data transfer object for category creation.

        Returns:
            ResultDTO: Operation result containing success status and data.
        """
        try:
            with SessionLocal() as db_session:
                model = CategoryMapper.to_model(dto)
                db_session.add(model)
                db_session.commit()
                db_session.refresh(model)
                return ResultDTO.success(
                    "Category created successfully",
                    CategoryMapper.to_dto(model),
                )
        except SQLAlchemyError as err:
            return ResultDTO.error(f"Failed to create category: {repr(err)}")

    def get_all(self) -> ResultDTO:
        """
        Retrieve all categories.

        Returns:
            ResultDTO: Operation result with list of categories.
        """
        try:
            with SessionLocal() as db_session:
                categories = db_session.query(Category).all()
                data = [CategoryMapper.to_dto(cat) for cat in categories]
                return ResultDTO.success("Categories retrieved successfully", data)
        except SQLAlchemyError as err:
            return ResultDTO.error(f"Failed to retrieve categories: {repr(err)}")

    def get_by_id(self, category_id: int) -> ResultDTO:
        """
        Retrieve a category by its ID.

        Args:
            category_id (int): Unique identifier of the category.

        Returns:
            ResultDTO: Operation result containing the category or error message.
        """
        try:
            with SessionLocal() as db_session:
                category = db_session.get(Category, category_id)
                if category:
                    return ResultDTO.success(
                        "Category found",
                        CategoryMapper.to_dto(category),
                    )
                return ResultDTO.error("Category not found")
        except SQLAlchemyError as err:
            return ResultDTO.error(f"Error retrieving category: {repr(err)}")

    def delete(self, category_id: int) -> ResultDTO:
        """
        Delete a category by its ID.

        Args:
            category_id (int): Unique identifier of the category to delete.

        Returns:
            ResultDTO: Operation result with success or failure message.
        """
        try:
            with SessionLocal() as db_session:
                category = db_session.get(Category, category_id)
                if not category:
                    return ResultDTO.error("Category not found")

                db_session.delete(category)
                db_session.commit()
                return ResultDTO.success("Category deleted successfully")
        except SQLAlchemyError as err:
            return ResultDTO.error(f"Failed to delete category: {repr(err)}")

    def get_by_name(self, category_name: str) -> ResultDTO:
        """
        Retrieve a category by its name.

        Args:
            category_name (str): Name of the category to search for.

        Returns:
            ResultDTO: Operation result containing the category or error message.
        """
        try:
            with SessionLocal() as db_session:
                category = (
                    db_session.query(Category)
                    .filter_by(name=category_name)
                    .first()
                )
                if category:
                    return ResultDTO.success(
                        "Category found",
                        CategoryMapper.to_dto(category),
                    )
                return ResultDTO.error("Category not found")
        except SQLAlchemyError as err:
            return ResultDTO.error(f"Error retrieving category: {repr(err)}")

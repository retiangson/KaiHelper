"""
CategoryMapper
Converts between Category ORM models and CategoryDTO objects.
"""

# --- First-party imports ---
from kaihelper.domain.models.category import Category
from kaihelper.contracts.category_dto import CategoryDTO


class CategoryMapper:
    """Mapper for converting between Category model and CategoryDTO."""

    @staticmethod
    def to_dto(model: Category) -> CategoryDTO:
        """
        Convert a Category ORM model to a CategoryDTO.

        Args:
            model (Category): ORM model instance representing a category record.

        Returns:
            CategoryDTO: Data transfer object representation of the model.
        """
        return CategoryDTO(
            category_id=model.category_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(dto: CategoryDTO) -> Category:
        """
        Convert a CategoryDTO to a Category ORM model.

        Args:
            dto (CategoryDTO): Data transfer object containing category details.

        Returns:
            Category: ORM model instance ready for database persistence.
        """
        model = Category()
        model.name = dto.name
        model.description = dto.description
        return model

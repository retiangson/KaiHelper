from kaihelper.domain.models.category import Category
from kaihelper.contracts.category_dto import CategoryDTO

class CategoryMapper:
    @staticmethod
    def to_dto(model: Category) -> CategoryDTO:
        return CategoryDTO(
            category_id=model.category_id,
            name=model.name,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    @staticmethod
    def to_model(dto: CategoryDTO) -> Category:
        model = Category()
        model.name = dto.name
        model.description = dto.description
        return model

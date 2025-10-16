from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.category import Category
from kaihelper.domain.mappers.category_mapper import CategoryMapper
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.category_dto import CategoryDTO

class CategoryRepository:
    """Repository for CRUD operations on Category."""

    def __init__(self):
        self.db = SessionLocal()

    def create(self, dto: CategoryDTO) -> ResultDTO:
        try:
            model = CategoryMapper.to_model(dto)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return ResultDTO(True, "Category created successfully", CategoryMapper.to_dto(model))
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to create category: {e}")
        finally:
            self.db.close()

    def get_all(self) -> ResultDTO:
        try:
            categories = self.db.query(Category).all()
            data = [CategoryMapper.to_dto(cat) for cat in categories]
            return ResultDTO.ok(True, "Categories retrieved successfully", data)
        except Exception as e:
            return ResultDTO.fail(False, f"Failed to retrieve categories: {e}")
        finally:
            self.db.close()

    def get_by_id(self, category_id: int) -> ResultDTO:
        try:
            category = self.db.query(Category).get(category_id)
            if category:
                return ResultDTO(True, "Category found", CategoryMapper.to_dto(category))
            return ResultDTO(False, "Category not found")
        except Exception as e:
            return ResultDTO(False, f"Error retrieving category: {e}")
        finally:
            self.db.close()

    def delete(self, category_id: int) -> ResultDTO:
        try:
            category = self.db.query(Category).get(category_id)
            if not category:
                return ResultDTO(False, "Category not found")
            self.db.delete(category)
            self.db.commit()
            return ResultDTO(True, "Category deleted successfully")
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to delete category: {e}")
        finally:
            self.db.close()
            
    def get_by_name(self, category_name: str) -> ResultDTO:
        try:
            category = self.db.query(Category).filter(Category.name == category_name).first()
            if category:
                return ResultDTO(True, "Category found", CategoryMapper.to_dto(category))
            return ResultDTO(False, "Category not found")
        except Exception as e:
            return ResultDTO(False, f"Error retrieving category: {e}")
        finally:
            self.db.close()

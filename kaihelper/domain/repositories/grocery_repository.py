"""
GroceryRepository
Handles database persistence for Grocery entities.
"""

from datetime import datetime
from kaihelper.domain.models.grocery import Grocery
from kaihelper.domain.mappers.grocery_mapper import GroceryMapper
from kaihelper.contracts.grocery_dto import GroceryDTO
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.interfaces.igrocery_repository import IGroceryRepository


class GroceryRepository(IGroceryRepository):
    """Repository class for CRUD operations on groceries."""

    def __init__(self):
        self.db = SessionLocal()

    # ------------------------------------------------------------------
    def create(self, dto: GroceryDTO) -> ResultDTO:
        """Create a new grocery record."""
        try:
            model = GroceryMapper.to_model(dto)
            self.db.add(model)
            return self._commit_and_return(model, "Grocery added successfully")
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to add grocery: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def update(self, dto: GroceryDTO) -> ResultDTO:
        """Update an existing grocery record."""
        try:
            grocery = self.db.query(Grocery).filter_by(grocery_id=dto.grocery_id).first()
            if not grocery:
                return ResultDTO(False, "Grocery not found")

            GroceryMapper.apply_updates(grocery, dto)
            return self._commit_and_return(grocery, "Grocery updated successfully")
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to update grocery: {e}")
        finally:
            self.db.close()


    # ------------------------------------------------------------------
    def get_by_name(self, user_id: int, item_name: str) -> ResultDTO:
        """Retrieve grocery by name for a specific user."""
        try:
            grocery = self.db.query(Grocery).filter_by(user_id=user_id, item_name=item_name).first()
            if grocery:
                return ResultDTO(True, "Grocery found", GroceryMapper.to_dto(grocery))
            return ResultDTO(False, "Grocery not found")
        except Exception as e:
            return ResultDTO(False, f"Failed to get grocery by name: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def get_all(self, user_id: int) -> ResultDTO:
        """Retrieve all groceries for a specific user."""
        try:
            groceries = self.db.query(Grocery).filter_by(user_id=user_id).all()
            data = [GroceryMapper.to_dto(g) for g in groceries]
            return ResultDTO(True, "Groceries retrieved successfully", data)
        except Exception as e:
            return ResultDTO(False, f"Failed to retrieve groceries: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def get_by_id(self, grocery_id: int) -> ResultDTO:
        """Retrieve a grocery record by ID."""
        try:
            grocery = self.db.query(Grocery).filter_by(grocery_id=grocery_id).first()
            if grocery:
                return ResultDTO(True, "Grocery retrieved successfully", GroceryMapper.to_dto(grocery))
            return ResultDTO(False, "Grocery not found")
        except Exception as e:
            return ResultDTO(False, f"Failed to retrieve grocery: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def delete(self, grocery_id: int) -> ResultDTO:
        """Delete a grocery record."""
        try:
            grocery = self.db.query(Grocery).filter_by(grocery_id=grocery_id).first()
            if not grocery:
                return ResultDTO(False, "Grocery not found")

            self.db.delete(grocery)
            return self._commit_and_return(None, "Grocery deleted successfully", refresh=False)
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to delete grocery: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def _commit_and_return(self, model, message: str, refresh: bool = True) -> ResultDTO:
        """
        Extracted helper method used by create/update/delete.
        Handles commit, refresh (optional), and standardized success response.
        """
        try:
            self.db.commit()
            if model and refresh:
                self.db.refresh(model)
                return ResultDTO(True, message, GroceryMapper.to_dto(model))
            return ResultDTO(True, message)
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Database operation failed: {e}")
        finally:
            self.db.close()
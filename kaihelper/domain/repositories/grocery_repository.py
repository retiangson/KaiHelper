"""
GroceryRepository
Handles database persistence for Grocery entities.
"""

# --- Third-party imports ---
from sqlalchemy.exc import SQLAlchemyError

# --- First-party imports ---
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.grocery import Grocery
from kaihelper.domain.mappers.grocery_mapper import GroceryMapper
from kaihelper.contracts.grocery_dto import GroceryDTO
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.domain.interfaces.i_grocery_repository import IGroceryRepository


class GroceryRepository(IGroceryRepository):
    """Repository for CRUD operations on Grocery entities."""

    def create(self, dto: GroceryDTO) -> ResultDTO:
        """
        Create a new grocery record.

        Args:
            dto (GroceryDTO): Grocery data transfer object.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            with SessionLocal() as db_session:
                model = GroceryMapper.to_model(dto)
                db_session.add(model)
                db_session.commit()
                db_session.refresh(model)
                return ResultDTO.ok(
                    "Grocery added successfully",
                    GroceryMapper.to_dto(model),
                )
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to add grocery: {repr(err)}")

    def update(self, dto: GroceryDTO) -> ResultDTO:
        """
        Update an existing grocery record.

        Args:
            dto (GroceryDTO): Updated grocery data.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            with SessionLocal() as db_session:
                grocery = db_session.query(Grocery).filter_by(
                    grocery_id=dto.grocery_id
                ).first()
                if not grocery:
                    return ResultDTO.fail("Grocery not found")

                GroceryMapper.apply_updates(grocery, dto)
                db_session.commit()
                db_session.refresh(grocery)
                return ResultDTO.ok(
                    "Grocery updated successfully",
                    GroceryMapper.to_dto(grocery),
                )
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to update grocery: {repr(err)}")

    def get_by_name(self, user_id: int, item_name: str) -> ResultDTO:
        """
        Retrieve a grocery item by its name for a specific user.

        Args:
            user_id (int): User identifier.
            item_name (str): Item name to search for.

        Returns:
            ResultDTO: Grocery record or not found message.
        """
        try:
            with SessionLocal() as db_session:
                grocery = db_session.query(Grocery).filter_by(
                    user_id=user_id, item_name=item_name
                ).first()
                if grocery:
                    return ResultDTO.ok(
                        "Grocery found",
                        GroceryMapper.to_dto(grocery),
                    )
                return ResultDTO.fail("Grocery not found")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to get grocery by name: {repr(err)}")

    def get_all(self, user_id: int) -> ResultDTO:
        """
        Retrieve all groceries for a specific user.

        Args:
            user_id (int): User identifier.

        Returns:
            ResultDTO: List of groceries.
        """
        try:
            with SessionLocal() as db_session:
                groceries = db_session.query(Grocery).filter_by(user_id=user_id).all()
                data = [GroceryMapper.to_dto(grocery) for grocery in groceries]
                return ResultDTO.ok("Groceries retrieved successfully", data)
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve groceries: {repr(err)}")

    def get_by_id(self, grocery_id: int) -> ResultDTO:
        """
        Retrieve a grocery record by its ID.

        Args:
            grocery_id (int): Grocery identifier.

        Returns:
            ResultDTO: Grocery record or not found message.
        """
        try:
            with SessionLocal() as db_session:
                grocery = db_session.get(Grocery, grocery_id)
                if grocery:
                    return ResultDTO.ok(
                        "Grocery retrieved successfully",
                        GroceryMapper.to_dto(grocery),
                    )
                return ResultDTO.fail("Grocery not found")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve grocery: {repr(err)}")

    def delete(self, grocery_id: int) -> ResultDTO:
        """
        Delete a grocery record by its ID.

        Args:
            grocery_id (int): Grocery identifier.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            with SessionLocal() as db_session:
                grocery = db_session.get(Grocery, grocery_id)
                if not grocery:
                    return ResultDTO.fail("Grocery not found")

                db_session.delete(grocery)
                db_session.commit()
                return ResultDTO.ok("Grocery deleted successfully")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to delete grocery: {repr(err)}")
        
    def get_by_expense_id(self, expense_id: int) -> ResultDTO:
        """
        Retrieve a grocery item linked to a specific expense record.

        Args:
            expense_id (int): Expense identifier.

        Returns:
            ResultDTO: Grocery data or error.
        """
        try:
            with SessionLocal() as db_session:
                groceries = db_session.query(Grocery).filter_by(expense_id=expense_id).all()
                data = [GroceryMapper.to_dto(grocery) for grocery in groceries]
                if groceries:
                    return ResultDTO.ok("Grocery found",data)
                return ResultDTO.fail("Grocery not found")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve grocery by expense ID: {repr(err)}")
        
    def get_by_id(self, grocery_id: int) -> ResultDTO:
        """
        Retrieve a grocery record by its ID.

        Args:
            grocery_id (int): Grocery identifier.

        Returns:
            ResultDTO: Grocery record or not found message.
        """
        try:
            with SessionLocal() as db_session:
                grocery = db_session.get(Grocery, grocery_id)
                if grocery:
                    return ResultDTO.ok(
                        "Grocery retrieved successfully",
                        GroceryMapper.to_dto(grocery),
                    )
                return ResultDTO.fail("Grocery not found")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve grocery: {repr(err)}")
    
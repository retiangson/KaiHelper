from kaihelper.domain.models.grocery import Grocery
from kaihelper.contracts.grocery_dto import GroceryDTO
from datetime import datetime


class GroceryMapper:
    @staticmethod
    def to_model(dto: GroceryDTO) -> Grocery:
        """Convert DTO → ORM Model for creation."""
        return Grocery(
            grocery_id=dto.grocery_id,
            user_id=dto.user_id,
            category_id=dto.category_id,
            item_name=dto.item_name,
            unit_price=dto.unit_price,
            quantity=dto.quantity,
            purchase_date=dto.purchase_date,
            notes=dto.notes,
            created_at=dto.created_at or datetime.now(),
            updated_at=dto.updated_at or datetime.now(),
            total_cost=dto.total_cost,
        )

    @staticmethod
    def to_dto(model: Grocery) -> GroceryDTO:
        """Convert ORM Model → DTO for API/Service layer."""
        return GroceryDTO(
            grocery_id=model.grocery_id,
            user_id=model.user_id,
            category_id=model.category_id,
            item_name=model.item_name,
            unit_price=model.unit_price,
            quantity=model.quantity,
            purchase_date=model.purchase_date,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at,
            total_cost=model.total_cost,
        )

    @staticmethod
    def apply_updates(model: Grocery, dto: GroceryDTO) -> Grocery:
        """Apply DTO → existing ORM Model field updates."""
        model.item_name = dto.item_name
        model.unit_price = dto.unit_price
        model.quantity = dto.quantity
        model.category_id = dto.category_id
        model.purchase_date = dto.purchase_date
        model.notes = dto.notes
        model.updated_at = dto.updated_at or datetime.now()
        model.total_cost = dto.total_cost or (dto.unit_price * dto.quantity)
        return model

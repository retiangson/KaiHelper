from kaihelper.domain.models.expense import Expense
from kaihelper.contracts.expense_dto import ExpenseDTO
from datetime import datetime


class ExpenseMapper:
    """Handles mapping between Expense ORM model and ExpenseDTO."""

    @staticmethod
    def to_model(dto: ExpenseDTO) -> Expense:
        """Convert DTO → ORM model."""
        return Expense(
            expense_id=dto.expense_id,
            user_id=dto.user_id,
            grocery_id=dto.grocery_id,
            category_id=dto.category_id,
            amount=dto.amount,
            description=dto.description,
            expense_date=dto.expense_date,
            created_at=dto.created_at or datetime.now(),
            updated_at=dto.updated_at or datetime.now(),
        )

    @staticmethod
    def to_dto(model: Expense) -> ExpenseDTO:
        """Convert ORM model → DTO."""
        return ExpenseDTO(
            expense_id=model.expense_id,
            user_id=model.user_id,
            grocery_id=model.grocery_id,
            category_id=model.category_id,
            amount=model.amount,
            description=model.description,
            expense_date=model.expense_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def apply_updates(model: Expense, dto: ExpenseDTO) -> Expense:
        """Apply DTO updates to an existing Expense model."""
        model.amount = dto.amount
        model.category_id = dto.category_id
        model.grocery_id = dto.grocery_id
        model.description = dto.description
        model.expense_date = dto.expense_date
        model.updated_at = dto.updated_at or datetime.now()
        return model

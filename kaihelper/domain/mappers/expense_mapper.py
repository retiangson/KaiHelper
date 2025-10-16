"""
ExpenseMapper
Handles conversion between Expense ORM model and ExpenseDTO.
"""

# --- Standard library imports ---
from datetime import datetime

# --- First-party imports ---
from kaihelper.domain.models.expense import Expense
from kaihelper.contracts.expense_dto import ExpenseDTO


class ExpenseMapper:
    """Mapper for converting between Expense ORM model and ExpenseDTO."""

    @staticmethod
    def to_model(dto: ExpenseDTO) -> Expense:
        """
        Convert an ExpenseDTO to an Expense ORM model.

        Args:
            dto (ExpenseDTO): Data transfer object containing expense details.

        Returns:
            Expense: ORM model instance representing the expense.
        """
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
        """
        Convert an Expense ORM model to an ExpenseDTO.

        Args:
            model (Expense): ORM model instance representing a database record.

        Returns:
            ExpenseDTO: Data transfer object representation of the model.
        """
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
        """
        Apply changes from an ExpenseDTO to an existing Expense ORM model.

        Args:
            model (Expense): Existing ORM model to update.
            dto (ExpenseDTO): Updated expense data.

        Returns:
            Expense: Updated ORM model instance.
        """
        model.amount = dto.amount
        model.category_id = dto.category_id
        model.grocery_id = dto.grocery_id
        model.description = dto.description
        model.expense_date = dto.expense_date
        model.updated_at = dto.updated_at or datetime.now()
        return model

"""
ExpenseMapper
Handles conversion between Expense ORM model and ExpenseDTO,
including extended receipt metadata fields.
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
            category_id=dto.category_id,
            amount=dto.amount,
            description=dto.description,
            expense_date=dto.expense_date,
            created_at=dto.created_at or datetime.now(),
            updated_at=dto.updated_at or datetime.now(),
            receipt_image=dto.receipt_image,
            notes=dto.notes,
            store_name=getattr(dto, "store_name", None),
            store_address=getattr(dto, "store_address", None),
            receipt_number=getattr(dto, "receipt_number", None),
            payment_method=getattr(dto, "payment_method", None),
            currency=getattr(dto, "currency", None),
            subtotal_amount=getattr(dto, "subtotal_amount", None),
            tax_amount=getattr(dto, "tax_amount", None),
            discount_amount=getattr(dto, "discount_amount", None),
            due_date=getattr(dto, "due_date", None),
            suggestion=getattr(dto, "suggestion", None),
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
            category_id=model.category_id,
            amount=model.amount,
            description=model.description,
            expense_date=model.expense_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            receipt_image=model.receipt_image,
            notes=model.notes,
            store_name=model.store_name,
            store_address=model.store_address,
            receipt_number=model.receipt_number,
            payment_method=model.payment_method,
            currency=model.currency,
            subtotal_amount=model.subtotal_amount,
            tax_amount=model.tax_amount,
            discount_amount=model.discount_amount,
            due_date=model.due_date,
            suggestion=model.suggestion,
            category_name=getattr(model.category, "name", None)
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
        model.description = dto.description
        model.expense_date = dto.expense_date
        model.receipt_image = dto.receipt_image
        model.notes = dto.notes
        model.store_name = getattr(dto, "store_name", model.store_name)
        model.store_address = getattr(dto, "store_address", model.store_address)
        model.receipt_number = getattr(dto, "receipt_number", model.receipt_number)
        model.payment_method = getattr(dto, "payment_method", model.payment_method)
        model.currency = getattr(dto, "currency", model.currency)
        model.subtotal_amount = getattr(dto, "subtotal_amount", model.subtotal_amount)
        model.tax_amount = getattr(dto, "tax_amount", model.tax_amount)
        model.discount_amount = getattr(dto, "discount_amount", model.discount_amount)
        model.due_date = getattr(dto, "due_date", model.due_date)
        model.suggestion = getattr(dto, "suggestion", model.suggestion)
        model.updated_at = dto.updated_at or datetime.now()
        return model

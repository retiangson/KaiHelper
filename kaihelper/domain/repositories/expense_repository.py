"""
ExpenseRepository
Handles database persistence for Expense entities.
"""

# --- Third-party imports ---
from sqlalchemy.exc import SQLAlchemyError

# --- First-party imports ---
from sqlalchemy.orm import joinedload
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.expense import Expense
from kaihelper.domain.mappers.expense_mapper import ExpenseMapper
from kaihelper.contracts.expense_dto import ExpenseDTO
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.domain.interfaces.i_expense_repository import IExpenseRepository


class ExpenseRepository(IExpenseRepository):
    """Repository for CRUD operations on Expense entities."""

    def create(self, dto: ExpenseDTO) -> ResultDTO:
        """
        Create a new expense record.

        Args:
            dto (ExpenseDTO): Expense data transfer object.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            with SessionLocal() as db_session:
                model = ExpenseMapper.to_model(dto)
                db_session.add(model)
                db_session.commit()
                db_session.refresh(model)
                return ResultDTO.ok(
                    "Expense added successfully",
                    ExpenseMapper.to_dto(model),
                )
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to add expense: {repr(err)}")

    def update(self, dto: ExpenseDTO) -> ResultDTO:
        """
        Update an existing expense record.

        Args:
            dto (ExpenseDTO): Updated expense data.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            with SessionLocal() as db_session:
                expense = db_session.query(Expense).filter_by(expense_id=dto.expense_id).first()
                if not expense:
                    return ResultDTO.fail("Expense not found")

                ExpenseMapper.apply_updates(expense, dto)
                db_session.commit()
                db_session.refresh(expense)
                return ResultDTO.ok(
                    "Expense updated successfully",
                    ExpenseMapper.to_dto(expense),
                )
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to update expense: {repr(err)}")

    def get_all(self, user_id: int) -> ResultDTO:
        """
        Retrieve all expenses for a given user.

        Args:
            user_id (int): User identifier.

        Returns:
            ResultDTO: List of expenses.
        """
        try:
            with SessionLocal() as db_session:
                expenses = db_session.query(Expense).options(joinedload(Expense.category)).filter_by(user_id=user_id).all()
                data = [ExpenseMapper.to_dto(expense) for expense in expenses]
                return ResultDTO.ok("Expenses retrieved successfully", data)
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve expenses: {repr(err)}")

    def get_by_id(self, expense_id: int) -> ResultDTO:
        """
        Retrieve an expense by its unique ID.

        Args:
            expense_id (int): Expense identifier.

        Returns:
            ResultDTO: Expense data or not found message.
        """
        try:
            with SessionLocal() as db_session:
                expense = db_session.get(
                    db_session.query(Expense)
                    .options(joinedload(Expense.category))  # ✅ eager load category
                    .filter(Expense.expense_id == expense_id)
                    .first()
                )
                if expense:
                    return ResultDTO.ok(
                        "Expense retrieved successfully",
                        ExpenseMapper.to_dto(expense),
                    )
                return ResultDTO.fail("Expense not found")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve expense: {repr(err)}")

    def get_by_grocery_id(self, grocery_id: int) -> ResultDTO:
        """
        Retrieve an expense linked to a specific grocery item.

        Args:
            grocery_id (int): Grocery identifier.

        Returns:
            ResultDTO: Expense data or error.
        """
        try:
            with SessionLocal() as db_session:
                expense = db_session.query(Expense).options(joinedload(Expense.category)).filter_by(grocery_id=grocery_id).first()
                if expense:
                    return ResultDTO.ok(
                        "Expense found",
                        ExpenseMapper.to_dto(expense),
                    )
                return ResultDTO.fail("Expense not found")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve expense by grocery ID: {repr(err)}")

    def delete(self, expense_id: int) -> ResultDTO:
        """
        Delete an expense record by ID.

        Args:
            expense_id (int): Expense identifier.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            with SessionLocal() as db_session:
                expense = db_session.get(Expense, expense_id)
                if not expense:
                    return ResultDTO.fail("Expense not found")

                db_session.delete(expense)
                db_session.commit()
                return ResultDTO.ok("Expense deleted successfully")
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to delete expense: {repr(err)}")

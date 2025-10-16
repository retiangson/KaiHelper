"""
ExpenseRepository
Handles database persistence for Expense entities.
"""

from datetime import datetime
from kaihelper.domain.models.expense import Expense
from kaihelper.domain.mappers.expense_mapper import ExpenseMapper
from kaihelper.contracts.expense_dto import ExpenseDTO
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.interfaces.iexpense_repository import IExpenseRepository


class ExpenseRepository(IExpenseRepository):
    """Repository class for CRUD operations on expenses."""

    def __init__(self):
        self.db = SessionLocal()

    # ------------------------------------------------------------------
    def create(self, dto: ExpenseDTO) -> ResultDTO:
        """Create a new expense record."""
        try:
            model = ExpenseMapper.to_model(dto)
            self.db.add(model)
            return self._commit_and_return(model, "Expense added successfully")
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to add expense: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def update(self, dto: ExpenseDTO) -> ResultDTO:
        """Update an existing expense record."""
        try:
            expense = self.db.query(Expense).filter_by(expense_id=dto.expense_id).first()
            if not expense:
                return ResultDTO(False, "Expense not found")

            ExpenseMapper.apply_updates(expense, dto)
            return self._commit_and_return(expense, "Expense updated successfully")
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to update expense: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def get_all(self, user_id: int) -> ResultDTO:
        """Retrieve all expenses for a specific user."""
        try:
            expenses = self.db.query(Expense).filter_by(user_id=user_id).all()
            data = [ExpenseMapper.to_dto(e) for e in expenses]
            return ResultDTO(True, "Expenses retrieved successfully", data)
        except Exception as e:
            return ResultDTO(False, f"Failed to retrieve expenses: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def get_by_id(self, expense_id: int) -> ResultDTO:
        """Retrieve an expense record by ID."""
        try:
            expense = self.db.query(Expense).filter_by(expense_id=expense_id).first()
            if expense:
                return ResultDTO(True, "Expense retrieved successfully", ExpenseMapper.to_dto(expense))
            return ResultDTO(False, "Expense not found")
        except Exception as e:
            return ResultDTO(False, f"Failed to retrieve expense: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def get_by_grocery_id(self, grocery_id: int) -> ResultDTO:
        """Retrieve an expense linked to a specific grocery item."""
        try:
            expense = self.db.query(Expense).filter_by(grocery_id=grocery_id).first()
            if expense:
                return ResultDTO(True, "Expense found", ExpenseMapper.to_dto(expense))
            return ResultDTO(False, "Expense not found")
        except Exception as e:
            return ResultDTO(False, f"Failed to retrieve expense by grocery ID: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def delete(self, expense_id: int) -> ResultDTO:
        """Delete an expense record by ID."""
        try:
            expense = self.db.query(Expense).filter_by(expense_id=expense_id).first()
            if not expense:
                return ResultDTO(False, "Expense not found")

            self.db.delete(expense)
            return self._commit_and_return(None, "Expense deleted successfully", refresh=False)
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Failed to delete expense: {e}")
        finally:
            self.db.close()

    # ------------------------------------------------------------------
    def _commit_and_return(self, model, message: str, refresh: bool = True) -> ResultDTO:
        """Handle commit, refresh, and standardized success response."""
        try:
            self.db.commit()
            if model and refresh:
                self.db.refresh(model)
                return ResultDTO(True, message, ExpenseMapper.to_dto(model))
            return ResultDTO(True, message)
        except Exception as e:
            self.db.rollback()
            return ResultDTO(False, f"Database operation failed: {e}")

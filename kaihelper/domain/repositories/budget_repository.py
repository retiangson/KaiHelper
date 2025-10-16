"""
BudgetRepository
Handles database persistence for Budget entities.
"""

# --- Standard library imports ---
# (none)

# --- Third-party imports ---
from sqlalchemy.exc import SQLAlchemyError

# --- First-party imports ---
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.budget import Budget
from kaihelper.domain.mappers.budget_mapper import BudgetMapper
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.budget_dto import BudgetDTO


class BudgetRepository:
    """Repository for handling CRUD operations on Budget entities."""

    def create(self, dto: BudgetDTO) -> ResultDTO:
        """
        Create a new budget record in the database.

        Args:
            dto (BudgetDTO): Data transfer object representing the new budget.

        Returns:
            ResultDTO: Operation result with success flag, message, and created data.
        """
        try:
            with SessionLocal() as db_session:
                model = BudgetMapper.to_model(dto)
                db_session.add(model)
                db_session.commit()
                db_session.refresh(model)
                return ResultDTO.ok(
                    "Budget created successfully",
                    BudgetMapper.to_dto(model),
                )
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to create budget: {repr(err)}")

    def get_active_budgets(self, user_id: int) -> ResultDTO:
        """
        Retrieve all active budgets for a given user.

        Args:
            user_id (int): Identifier of the user whose budgets to retrieve.

        Returns:
            ResultDTO: Operation result with success flag, message, and data list.
        """
        try:
            with SessionLocal() as db_session:
                budgets = db_session.query(Budget).filter_by(user_id=user_id).all()
                data = [BudgetMapper.to_dto(budget) for budget in budgets]
                return ResultDTO.ok(
                    "Budgets retrieved successfully",
                    data,
                )
        except SQLAlchemyError as err:
            return ResultDTO.fail(f"Failed to retrieve budgets: {repr(err)}")

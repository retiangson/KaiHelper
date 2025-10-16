"""
BudgetService
Implements business logic for Budget operations.
"""

# --- Standard library imports ---
from datetime import date

# --- First-party imports ---
from kaihelper.business.interfaces.ibudget_service import IBudgetService
from kaihelper.domain.repositories.budget_repository import BudgetRepository
from kaihelper.contracts.budget_dto import BudgetDTO
from kaihelper.contracts.result_dto import ResultDTO


class BudgetService(IBudgetService):
    """Service layer implementing business rules for Budget operations."""

    def __init__(self, repository: BudgetRepository | None = None) -> None:
        """
        Initialize BudgetService with a BudgetRepository.

        Args:
            repository (BudgetRepository | None): Optional repository instance for dependency injection.
        """
        self._repo = repository or BudgetRepository()

    def create_budget(self, dto: BudgetDTO) -> ResultDTO:
        """
        Validate and create a new budget.

        Args:
            dto (BudgetDTO): Budget data transfer object.

        Returns:
            ResultDTO: Operation result with validation messages or success response.
        """
        if dto.total_budget <= 0:
            return ResultDTO(False, "Total budget must be greater than zero.")
        if dto.start_date >= dto.end_date:
            return ResultDTO(False, "End date must be after start date.")
        if dto.start_date < date.today():
            return ResultDTO(False, "Start date cannot be in the past.")

        dto.remaining_balance = dto.total_budget
        return self._repo.create(dto)

    def list_budgets(self, user_id: int) -> ResultDTO:
        """
        Retrieve all active budgets for a user.

        Args:
            user_id (int): Unique identifier for the user.

        Returns:
            ResultDTO: Result containing list of budgets or an error message.
        """
        if not user_id:
            return ResultDTO(False, "User ID is required.")

        return self._repo.get_active_budgets(user_id)

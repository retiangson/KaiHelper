from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.budget_dto import BudgetDTO

class IBudgetRepository(ABC):
    """Interface for budget repository operations."""

    @abstractmethod
    def create(self, dto: BudgetDTO) -> ResultDTO:
        pass

    @abstractmethod
    def get_active_budgets(self, user_id: int) -> ResultDTO:
        pass

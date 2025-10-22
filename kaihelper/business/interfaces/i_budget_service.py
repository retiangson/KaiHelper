from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.budget_dto import BudgetDTO

class IBudgetService(ABC):
    """Interface for budget business logic."""

    @abstractmethod
    def create_budget(self, dto: BudgetDTO) -> ResultDTO:
        pass

    @abstractmethod
    def list_budgets(self, user_id: int) -> ResultDTO:
        pass

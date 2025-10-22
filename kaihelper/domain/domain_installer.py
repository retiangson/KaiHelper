"""
Domain Installer: binds interfaces to repositories.
"""
from typing import Type, Dict, Any

# Existing user repository
from kaihelper.domain.repositories.user_repository import UserRepository
from kaihelper.domain.interfaces.i_user_repository import IUserRepository

# New repositories
from kaihelper.domain.repositories.category_repository import CategoryRepository
from kaihelper.domain.repositories.grocery_repository import GroceryRepository
from kaihelper.domain.repositories.budget_repository import BudgetRepository
from kaihelper.domain.repositories.expense_repository import ExpenseRepository

# New repository interfaces
from kaihelper.domain.interfaces.i_category_repository import ICategoryRepository
from kaihelper.domain.interfaces.i_grocery_repository import IGroceryRepository
from kaihelper.domain.interfaces.i_budget_repository import IBudgetRepository
from kaihelper.domain.interfaces.i_expense_repository import IExpenseRepository


class DomainInstaller:
    """Responsible for binding repository interfaces to their implementations."""

    def __init__(self):
        self._repo_map: Dict[Type, Any] = {}
        self._register_repositories()

    def _register_repositories(self) -> None:
        """Registers all repositories."""
        self._repo_map[IUserRepository] = UserRepository()
        self._repo_map[ICategoryRepository] = CategoryRepository()
        self._repo_map[IGroceryRepository] = GroceryRepository()
        self._repo_map[IBudgetRepository] = BudgetRepository()
        self._repo_map[IExpenseRepository] = ExpenseRepository()

    def resolve(self, interface: Type) -> Any:
        """Resolves a repository implementation by its interface."""
        if (repo := self._repo_map.get(interface)) is not None:
            return repo
        raise ValueError(f"Repository for {interface.__name__} not registered.")

    # Convenience getters
    def get_user_repository(self) -> IUserRepository:
        return self.resolve(IUserRepository)

    def get_category_repository(self) -> ICategoryRepository:
        return self.resolve(ICategoryRepository)

    def get_grocery_repository(self) -> IGroceryRepository:
        return self.resolve(IGroceryRepository)

    def get_budget_repository(self) -> IBudgetRepository:
        return self.resolve(IBudgetRepository)

    def get_expense_repository(self) -> IExpenseRepository:
        return self.resolve(IExpenseRepository)

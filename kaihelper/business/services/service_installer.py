"""
Service Installer
Binds service interfaces to their concrete implementations and injects dependencies.
"""

from typing import Type, Dict, Any

# Domain installer provides repositories
from kaihelper.domain.domain_installer import DomainInstaller

# Service interfaces
from kaihelper.business.interfaces.i_user_service import IUserService
from kaihelper.business.interfaces.icategory_service import ICategoryService
from kaihelper.business.interfaces.igrocery_service import IGroceryService
from kaihelper.business.interfaces.ibudget_service import IBudgetService
from kaihelper.business.interfaces.iexpense_service import IExpenseService
from kaihelper.business.interfaces.i_receipt_service import IReceiptService

# Repository interfaces
from kaihelper.domain.interfaces.i_user_repository import IUserRepository
from kaihelper.domain.interfaces.icategory_repository import ICategoryRepository
from kaihelper.domain.interfaces.igrocery_repository import IGroceryRepository
from kaihelper.domain.interfaces.ibudget_repository import IBudgetRepository
from kaihelper.domain.interfaces.iexpense_repository import IExpenseRepository


class ServiceInstaller:
    """Responsible for binding service interfaces to their implementations."""

    def __init__(self, domain_installer: DomainInstaller):
        self._domain = domain_installer
        self._service_map: Dict[Type, Any] = {}
        self._register_services()

    # ------------------------------------------------------------------
    def _register_services(self) -> None:
        """Registers all services with their corresponding dependencies."""
        # --- Lazy imports to prevent circular imports ---
        from kaihelper.business.services.user_service import UserService
        from kaihelper.business.services.category_service import CategoryService
        from kaihelper.business.services.grocery_service import GroceryService
        from kaihelper.business.services.budget_service import BudgetService
        from kaihelper.business.services.expense_service import ExpenseService
        from kaihelper.business.services.receipt_service import ReceiptService

        # --- Repository bindings from Domain Layer ---
        user_repo: IUserRepository = self._domain.get_user_repository()
        category_repo: ICategoryRepository = self._domain.get_category_repository()
        grocery_repo: IGroceryRepository = self._domain.get_grocery_repository()
        budget_repo: IBudgetRepository = self._domain.get_budget_repository()
        expense_repo: IExpenseRepository = self._domain.get_expense_repository()

        # --- Service Bindings ---
        self._service_map[IUserService] = UserService(user_repo)
        self._service_map[ICategoryService] = CategoryService(category_repo)
        self._service_map[IGroceryService] = GroceryService(grocery_repo)
        self._service_map[IBudgetService] = BudgetService(budget_repo)
        self._service_map[IExpenseService] = ExpenseService(expense_repo)

        # --- Receipt Service ---
        # Injects the GroceryService and ExpenseService instances
        category_service = self._service_map[ICategoryService]
        grocery_service = self._service_map[IGroceryService]
        expense_service = self._service_map[IExpenseService]
        
        self._service_map[IReceiptService] = ReceiptService(
            category_service=category_service,
            grocery_service=grocery_service,
            expense_service=expense_service,
        )

    # ------------------------------------------------------------------
    def resolve(self, interface: Type) -> Any:
        """Resolves a service implementation by its interface."""
        if (service := self._service_map.get(interface)) is not None:
            return service
        raise ValueError(f"Service for {interface.__name__} not registered.")

    # ------------------------------------------------------------------
    # Convenience getters
    def get_user_service(self) -> IUserService:
        return self.resolve(IUserService)

    def get_category_service(self) -> ICategoryService:
        return self.resolve(ICategoryService)

    def get_grocery_service(self) -> IGroceryService:
        return self.resolve(IGroceryService)

    def get_budget_service(self) -> IBudgetService:
        return self.resolve(IBudgetService)

    def get_expense_service(self) -> IExpenseService:
        return self.resolve(IExpenseService)

    def get_receipt_service(self) -> IReceiptService:
        return self.resolve(IReceiptService)

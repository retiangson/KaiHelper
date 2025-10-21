"""
Service Installer
Binds service interfaces to their concrete implementations and injects dependencies.
Ensures consistent dependency resolution across the business layer.
"""

# --- Standard library imports ---
from typing import Type, Dict, Any

# --- First-party imports ---
from kaihelper.domain.domain_installer import DomainInstaller

# --- Service Interfaces ---
from kaihelper.business.interfaces.i_user_service import IUserService
from kaihelper.business.interfaces.i_category_service import ICategoryService
from kaihelper.business.interfaces.i_grocery_service import IGroceryService
from kaihelper.business.interfaces.i_budget_service import IBudgetService
from kaihelper.business.interfaces.i_expense_service import IExpenseService
from kaihelper.business.interfaces.i_receipt_service import IReceiptService

# --- Repository Interfaces ---
from kaihelper.domain.interfaces.i_user_repository import IUserRepository
from kaihelper.domain.interfaces.i_category_repository import ICategoryRepository
from kaihelper.domain.interfaces.i_grocery_repository import IGroceryRepository
from kaihelper.domain.interfaces.i_budget_repository import IBudgetRepository
from kaihelper.domain.interfaces.i_expense_repository import IExpenseRepository


class ServiceInstaller:
    """
    Responsible for binding service interfaces to their concrete implementations.
    Provides a central container for dependency injection within the business layer.
    """

    def __init__(self, domain_installer: DomainInstaller) -> None:
        """
        Initialize the service installer.

        Args:
            domain_installer (DomainInstaller): Provides repository instances for dependency injection.
        """
        self._domain = domain_installer
        self._service_map: Dict[Type, Any] = {}
        self._register_services()

    def _register_services(self) -> None:
        """
        Register all services and wire them with their respective repositories.
        Uses lazy imports to avoid circular dependencies between modules.
        """
        # --- Lazy imports (to prevent circular references) ---
        from kaihelper.business.services.user_service import UserService
        from kaihelper.business.services.category_service import CategoryService
        from kaihelper.business.services.grocery_service import GroceryService
        from kaihelper.business.services.budget_service import BudgetService
        from kaihelper.business.services.expense_service import ExpenseService
        from kaihelper.business.services.receipt_service import ReceiptService

        # --- Repository bindings (from Domain Layer) ---
        user_repo: IUserRepository = self._domain.get_user_repository()
        category_repo: ICategoryRepository = self._domain.get_category_repository()
        grocery_repo: IGroceryRepository = self._domain.get_grocery_repository()
        budget_repo: IBudgetRepository = self._domain.get_budget_repository()
        expense_repo: IExpenseRepository = self._domain.get_expense_repository()

        # --- Core service bindings ---
        self._service_map[IUserService] = UserService(user_repo)
        self._service_map[ICategoryService] = CategoryService(category_repo)
        self._service_map[IGroceryService] = GroceryService(grocery_repo)
        self._service_map[IBudgetService] = BudgetService(budget_repo)
        self._service_map[IExpenseService] = ExpenseService(expense_repo)

        # --- Receipt Service (multi-dependency injection) ---
        category_service = self._service_map[ICategoryService]
        grocery_service = self._service_map[IGroceryService]
        expense_service = self._service_map[IExpenseService]

        self._service_map[IReceiptService] = ReceiptService(
            category_service=category_service,
            grocery_service=grocery_service,
            expense_service=expense_service,
        )

    def resolve(self, interface: Type) -> Any:
        """
        Retrieve a registered service implementation by its interface type.

        Args:
            interface (Type): Interface class to resolve.

        Returns:
            Any: The resolved service instance.

        Raises:
            ValueError: If no service is registered for the specified interface.
        """
        if (service := self._service_map.get(interface)) is not None:
            return service
        raise ValueError(f"Service for {interface.__name__} not registered.")

    # ------------------------------------------------------------------
    # Convenience Getters
    # ------------------------------------------------------------------

    def get_user_service(self) -> IUserService:
        """Return the registered UserService instance."""
        return self.resolve(IUserService)

    def get_category_service(self) -> ICategoryService:
        """Return the registered CategoryService instance."""
        return self.resolve(ICategoryService)

    def get_grocery_service(self) -> IGroceryService:
        """Return the registered GroceryService instance."""
        return self.resolve(IGroceryService)

    def get_budget_service(self) -> IBudgetService:
        """Return the registered BudgetService instance."""
        return self.resolve(IBudgetService)

    def get_expense_service(self) -> IExpenseService:
        """Return the registered ExpenseService instance."""
        return self.resolve(IExpenseService)

    def get_receipt_service(self) -> IReceiptService:
        """Return the registered ReceiptService instance."""
        return self.resolve(IReceiptService)

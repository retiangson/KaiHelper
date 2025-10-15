"""
User Service Interface
----------------------
Defines the contract for all UserService implementations.
"""

from abc import ABC, abstractmethod
from kaihelper.contracts.user_dto import RegisterUserDTO, LoginRequestDTO
from kaihelper.contracts.result_dto import ResultDTO


class IUserService(ABC):
    """Abstract interface for user-related operations."""

    @abstractmethod
    def register_user(self, dto: RegisterUserDTO) -> ResultDTO:
        """Registers a new user."""
        pass

    @abstractmethod
    def login_user(self, dto: LoginRequestDTO) -> ResultDTO:
        """Authenticates an existing user."""
        pass

    @abstractmethod
    def get_user_profile(self, user_id: int) -> ResultDTO:
        """Fetches the user profile by ID."""
        pass

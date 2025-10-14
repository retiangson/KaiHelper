"""
User Repository Interface
-------------------------
Defines the contract for user data access operations.
"""

from abc import ABC, abstractmethod
from kaihelper.contracts.user_dto import RegisterUserDTO, UserDTO
from kaihelper.contracts.result_dto import ResultDTO


class IUserRepository(ABC):
    """Abstract interface for user data persistence."""

    @abstractmethod
    def create_user(self, dto: RegisterUserDTO) -> ResultDTO:
        """Inserts a new user record."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str):
        """Fetches a user by email (returns domain model or dict)."""
        pass

    @abstractmethod
    def get_username_or_email(self, username_or_email: str, password: str) -> UserDTO:
        """Fetches a user by username or email and verifies the password."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int):
        """Fetches a user by ID."""
        pass

    @abstractmethod
    def verify_credentials(self, username_or_email: str, password: str) -> dict | None:
        """Verifies user credentials for login."""
        pass

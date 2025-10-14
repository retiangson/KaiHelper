"""
UserMapper Module
-----------------
Handles conversion between User domain model and UserDTO.

"""

from kaihelper.domain.models.user import User
from kaihelper.contracts.user_dto import UserDTO
from datetime import datetime

class UserMapper:
    """Maps between User entity and UserDTO."""

    @staticmethod
    def to_dto(user: User) -> UserDTO | None:
        """Converts a User model instance to a UserDTO."""
        if not user:
            return None

        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    @staticmethod
    def to_entity(dto) -> User | None:
        """Converts any user-related DTO to a User entity."""
        if not dto:
            return None

        user = User(
            username=getattr(dto, "username", None),
            email=getattr(dto, "email", None),
            password=getattr(dto, "password", None),
            is_active=getattr(dto, "is_active", True),
            created_at=getattr(dto, "created_at", datetime.utcnow()),
            updated_at=getattr(dto, "updated_at", datetime.utcnow()),
        )

        return user

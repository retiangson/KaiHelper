"""
UserMapper
Converts between User ORM model and UserDTO objects.
"""

# --- Standard library imports ---
from datetime import datetime, timezone

# --- First-party imports ---
from kaihelper.domain.models.user import User
from kaihelper.contracts.user_dto import UserDTO


class UserMapper:
    """Mapper for converting between User entity and UserDTO."""

    @staticmethod
    def to_dto(user: User) -> UserDTO | None:
        """
        Convert a User ORM model instance to a UserDTO.

        Args:
            user (User): ORM model instance representing a user.

        Returns:
            UserDTO | None: Data transfer object for the user, or None if input is invalid.
        """
        if not user:
            return None

        return UserDTO(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @staticmethod
    def to_entity(dto: UserDTO) -> User:
        """
        Convert a UserDTO into a User ORM entity.

        Args:
            dto (UserDTO): Data transfer object containing user information.

        Returns:
            User: ORM model instance ready for database persistence.
        """
        return User(
            username=getattr(dto, "username", None),
            email=getattr(dto, "email", None),
            password=getattr(dto, "password", None),
            is_active=getattr(dto, "is_active", True),
            created_at=getattr(dto, "created_at", datetime.now(timezone.utc)),
            updated_at=getattr(dto, "updated_at", datetime.now(timezone.utc)),
        )

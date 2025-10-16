"""
UserRepository (SQLAlchemy)
Handles CRUD operations and authentication for User entities.
- Hashes passwords (PBKDF2-SHA256)
- Enforces unique email/username
- Provides secure credential verification
"""

from typing import Optional, Dict, Any

# --- Third-party imports ---
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# --- First-party imports ---
from kaihelper.domain.mappers.user_mapper import UserMapper
from kaihelper.domain.interfaces.i_user_repository import IUserRepository
from kaihelper.contracts.user_dto import RegisterUserDTO, UserDTO
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.user import User

class UserRepository(IUserRepository):
    """Repository for CRUD and authentication operations on User."""

    @staticmethod
    def _to_public_dict(user: User) -> Dict[str, Any]:
        """
        Convert a User ORM object to a public-safe dictionary.

        Args:
            user (User): User model instance.

        Returns:
            dict: Dictionary containing non-sensitive user data.
        """
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
        }

    def create_user(self, dto: RegisterUserDTO) -> ResultDTO:
        """
        Create a new user account.

        Args:
            dto (RegisterUserDTO): Data Transfer Object for registration.

        Returns:
            ResultDTO: Operation result.
        """
        try:
            with SessionLocal() as db_session:
                new_user = UserMapper.to_entity(dto)
                db_session.add(new_user)
                db_session.commit()
                db_session.refresh(new_user)
                return ResultDTO.success(
                    "User registered successfully",
                    self._to_public_dict(new_user),
                )
        except IntegrityError as err:
            msg = str(getattr(err, "orig", err)).lower()
            if "email" in msg:
                return ResultDTO.error(f"Email '{dto.email}' already exists.")
            if "username" in msg:
                return ResultDTO.error(f"Username '{dto.username}' already exists.")
            return ResultDTO.error("Unique constraint violated.")
        except SQLAlchemyError as err:
            return ResultDTO.error(f"Failed to register user: {repr(err)}")

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """
        Retrieve a user by email.

        Args:
            email (str): Email address.

        Returns:
            dict | None: User dictionary or None if not found.
        """
        try:
            with SessionLocal() as db_session:
                user = db_session.query(User).filter_by(email=email).first()
                return self._to_public_dict(user) if user else None
        except SQLAlchemyError:
            return None

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """
        Retrieve a user by ID.

        Args:
            user_id (int): User identifier.

        Returns:
            dict | None: User dictionary or None if not found.
        """
        try:
            with SessionLocal() as db_session:
                user = db_session.get(User, user_id)
                return self._to_public_dict(user) if user else None
        except SQLAlchemyError:
            return None

    def get_username_or_email(
        self, username_or_email: str, password: str
    ) -> Optional[UserDTO]:
        """
        Retrieve and verify a user by username or email.

        Args:
            username_or_email (str): Username or email.
            password (str): Plain-text password.

        Returns:
            UserDTO | None: User DTO if valid credentials, None otherwise.
        """
        try:
            with SessionLocal() as db_session:
                user = (
                    db_session.query(User)
                    .filter(
                        (User.email == username_or_email)
                        | (User.username == username_or_email)
                    )
                    .first()
                )
                if not user or not pbkdf2_sha256.verify(password, user.password):
                    return None
                return UserMapper.to_dto(user)
        except SQLAlchemyError:
            return None

    def verify_credentials(
        self, username_or_email: str, password: str
    ) -> Optional[UserDTO]:
        """
        Verify login credentials.

        Args:
            username_or_email (str): Username or email input.
            password (str): Plain-text password.

        Returns:
            UserDTO | None: User DTO if valid, None otherwise.
        """
        try:
            with SessionLocal() as db_session:
                user = (
                    db_session.query(User)
                    .filter(
                        (User.email == username_or_email)
                        | (User.username == username_or_email)
                    )
                    .first()
                )
                if not user or not pbkdf2_sha256.verify(password, user.password):
                    return None
                return UserMapper.to_dto(user)
        except SQLAlchemyError:
            return None

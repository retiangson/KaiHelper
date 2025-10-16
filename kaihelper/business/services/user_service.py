"""
UserService
Implements user registration, authentication, and profile retrieval logic.
"""

# --- Third-party imports ---
from passlib.hash import pbkdf2_sha256

# --- First-party imports ---
from kaihelper.business.interfaces.i_user_service import IUserService
from kaihelper.domain.interfaces.i_user_repository import IUserRepository
from kaihelper.contracts.user_dto import RegisterUserDTO, LoginRequestDTO
from kaihelper.contracts.result_dto import ResultDTO


class UserService(IUserService):
    """Business logic layer for user management and authentication."""

    def __init__(self, user_repo: IUserRepository) -> None:
        """
        Initialize the UserService with a repository dependency.

        Args:
            user_repo (IUserRepository): Repository instance for user persistence operations.
        """
        self._user_repo = user_repo

    def register_user(self, dto: RegisterUserDTO) -> ResultDTO:
        """
        Register a new user after validation and password hashing.

        Args:
            dto (RegisterUserDTO): Registration data transfer object.

        Returns:
            ResultDTO: Operation result indicating success or failure.
        """
        if dto.password != dto.confirm_password:
            return ResultDTO.error("Passwords do not match")

        if getattr(dto, "password", None):
            dto.password = pbkdf2_sha256.hash(dto.password)

        return self._user_repo.create_user(dto)

    def login_user(self, dto: LoginRequestDTO) -> ResultDTO:
        """
        Authenticate a user by verifying username or email and password.

        Args:
            dto (LoginRequestDTO): Login request data transfer object.

        Returns:
            ResultDTO: Operation result with user data or error message.
        """
        user = self._user_repo.verify_credentials(dto.username_or_email, dto.password)
        if user:
            return ResultDTO.success("Login successful", data=user)
        return ResultDTO.error("Invalid credentials")

    def get_user_profile(self, user_id: int) -> ResultDTO:
        """
        Retrieve a user's profile by their unique ID.

        Args:
            user_id (int): User identifier.

        Returns:
            ResultDTO: Operation result with user data or error message.
        """
        user = self._user_repo.get_user_by_id(user_id)
        if user:
            return ResultDTO.success("Profile retrieved", data=user)
        return ResultDTO.error("User not found")

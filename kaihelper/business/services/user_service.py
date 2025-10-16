from kaihelper.business.interfaces.i_user_service import IUserService
from kaihelper.domain.interfaces.i_user_repository import IUserRepository
from kaihelper.contracts.user_dto import RegisterUserDTO, LoginRequestDTO
from kaihelper.contracts.result_dto import ResultDTO
from passlib.hash import bcrypt
from passlib.hash import pbkdf2_sha256

class UserService(IUserService):
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo

    def register_user(self, dto: RegisterUserDTO) -> ResultDTO:
        """Register a new user after validating and hashing the password."""

        if dto.password != dto.confirm_password:
            return ResultDTO(False, "Passwords do not match")
        
        if getattr(dto, "password", None):
            dto.password = pbkdf2_sha256.hash(dto.password)

        return self._user_repo.create_user(dto)

    def login_user(self, dto: LoginRequestDTO) -> ResultDTO:
        """Authenticate user by verifying username and password."""

        if (user := self._user_repo.verify_credentials(dto.username_or_email, dto.password)):
            return ResultDTO(True, "Login successful", data=user)
        else:
            return ResultDTO(False, "Invalid credentials")

    def get_user_profile(self, user_id: int) -> ResultDTO:
        if (user := self._user_repo.get_user_by_id(user_id)):
            return ResultDTO(True, "Profile retrieved", data=user)
        else:
            return ResultDTO(False, "User not found")


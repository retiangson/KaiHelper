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
        return self._user_repo.create_user(dto)

    def login_user(self, dto: LoginRequestDTO) -> ResultDTO:
        """Authenticate user by verifying username and password."""

        user = self._user_repo.verify_credentials(dto.username_or_email, dto.password)

        if not user:
            return ResultDTO(False, "Invalid credentials")
        return ResultDTO(True, "Login successful", data=user)

    def get_user_profile(self, user_id: int) -> ResultDTO:
        user = self._user_repo.get_user_by_id(user_id)
        if not user:
            return ResultDTO(False, "User not found")
        return ResultDTO(True, "Profile retrieved", data=user)

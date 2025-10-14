"""
Domain Installer: binds interfaces to repositories.
"""
from typing import Type, Dict, Any
from kaihelper.domain.repository.user_repository import UserRepository
from kaihelper.domain.interfaces.i_user_repository import IUserRepository

class DomainInstaller:
    def __init__(self):
        self._repo_map: Dict[Type, Any] = {}
        self._register_repositories()

    def _register_repositories(self):
        self._repo_map[IUserRepository] = UserRepository()

    def resolve(self, interface: Type):
        repo = self._repo_map.get(interface)
        if not repo:
            raise ValueError(f"Repository for {interface.__name__} not registered.")
        return repo

    # Convenience
    def get_user_repository(self) -> IUserRepository:
        return self.resolve(IUserRepository)

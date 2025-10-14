"""
Service Installer: binds interfaces to services.
"""
from typing import Type, Dict, Any
from kaihelper.business.service.user_service import UserService
from kaihelper.business.interfaces.i_user_service import IUserService
from kaihelper.domain.domain_installer import DomainInstaller
from kaihelper.domain.interfaces.i_user_repository import IUserRepository

class ServiceInstaller:
    def __init__(self, domain_installer: DomainInstaller):
        self._domain = domain_installer
        self._service_map: Dict[Type, Any] = {}
        self._register_services()

    def _register_services(self):
        user_repo: IUserRepository = self._domain.get_user_repository()
        self._service_map[IUserService] = UserService(user_repo)

    def resolve(self, interface: Type):
        service = self._service_map.get(interface)
        if not service:
            raise ValueError(f"Service for {interface.__name__} not registered.")
        return service

    # Convenience
    def get_user_service(self) -> IUserService:
        return self.resolve(IUserService)

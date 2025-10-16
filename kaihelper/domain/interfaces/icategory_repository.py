from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.category_dto import CategoryDTO

class ICategoryRepository(ABC):
    """Interface for category repository operations."""

    @abstractmethod
    def create(self, dto: CategoryDTO) -> ResultDTO:
        pass

    @abstractmethod
    def get_all(self) -> ResultDTO:
        pass

    @abstractmethod
    def get_by_id(self, category_id: int) -> ResultDTO:
        pass

    @abstractmethod
    def get_by_name(self, category_name: str) -> ResultDTO:
        pass

    @abstractmethod
    def delete(self, category_id: int) -> ResultDTO:
        pass

from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.contracts.category_dto import CategoryDTO

class ICategoryService(ABC):
    """Interface for category business logic."""

    @abstractmethod
    def add_category(self, dto: CategoryDTO) -> ResultDTO:
        pass

    @abstractmethod
    def list_categories(self) -> ResultDTO:
        pass
    
    @abstractmethod
    def delete_category(self, category_id: int) -> ResultDTO:
        pass

    @abstractmethod
    def get_category(self, category_name: str) -> ResultDTO:
        pass

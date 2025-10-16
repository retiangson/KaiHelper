"""
IReceiptService Interface
Defines the contract for receipt processing services.
"""

from abc import ABC, abstractmethod
from kaihelper.contracts.result_dto import ResultDTO


class IReceiptService(ABC):
    """Abstract base class for Receipt Service."""

    @abstractmethod
    def process_receipt(self, user_id: int, image_bytes: bytes) -> ResultDTO:
        """
        Analyze a receipt image and map extracted items to groceries and expenses.

        Args:
            user_id (int): ID of the user who uploaded the receipt.
            image_bytes (bytes): Binary content of the uploaded receipt image.

        Returns:
            ResultDTO: A standardized response containing the parsed receipt data.
        """
        pass

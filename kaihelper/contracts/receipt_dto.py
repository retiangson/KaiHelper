from typing import List, Optional
from pydantic import BaseModel

class ExtractedItemDTO(BaseModel):
    item_name: str
    quantity: float  # ✅ allow fractional values
    unit_price: float
    category: Optional[str] = "Uncategorized"

class ReceiptUploadResponseDTO(BaseModel):
    items: List[ExtractedItemDTO]
    total_amount: float

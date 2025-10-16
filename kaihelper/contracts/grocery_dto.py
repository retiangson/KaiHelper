from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class GroceryDTO:
    grocery_id: Optional[int] = None           # ✅ default None for new records
    user_id: int = 0
    category_id: Optional[int] = None          # ✅ allow None until categorized
    item_name: str = ""
    unit_price: float = 0.0
    quantity: float = 1.0                      # ✅ allow fractional later
    purchase_date: date = date.today()
    notes: Optional[str] = None                # ✅ optional for auto-added items
    created_at: Optional[date] = None
    updated_at: Optional[date] = None
    receipt_image: Optional[str] = None        # URL or path to the receipt image
    total_cost: Optional[float] = None         # Computed as unit_price * quantity
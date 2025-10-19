"""
CategoryDTO
Data Transfer Object for category information shared across application layers.
"""

# --- Standard library imports ---
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CategoryDTO:
    """
    Represents a category used to group expenses or groceries.

    Attributes:
        category_id (int | None): Unique identifier for the category.
        name (str): Category name (e.g., Groceries, Bills, Dining).
        description (str | None): Optional category description.
        created_at (datetime | None): Timestamp when the category was created.
        updated_at (datetime | None): Timestamp when the category was last updated.
    """
    category_id: int | None = None
    name: str = ""
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    

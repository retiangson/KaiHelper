"""
contracts/result_dto.py
Represents a standardized result or response across layers.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class ResultDTO:
    """Generic operation result for repository/service responses."""
    success: bool
    message: str
    data: Optional[Any] = None

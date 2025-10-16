"""
ResultDTO
Standardized response object used across KaiHelper services and APIs.
"""

# --- Standard library imports ---
from dataclasses import dataclass, asdict
from typing import Any, Optional


@dataclass
class ResultDTO:
    """
    Represents a standardized response wrapper for operations and API endpoints.

    Attributes:
        success (bool): Indicates whether the operation succeeded.
        message (str): Description or feedback message for the operation.
        data (Any | None): Optional payload or result data.
        code (int | None): Optional HTTP-style status code (e.g., 200, 400).
    """

    success: bool
    message: str
    data: Optional[Any] = None
    code: Optional[int] = None

    # ------------------------------------------------------------------
    # Factory Methods
    # ------------------------------------------------------------------

    @staticmethod
    def ok(message: str, data: Any = None, code: int = 200) -> "ResultDTO":
        """
        Create a successful result object.

        Args:
            message (str): Success message.
            data (Any, optional): Optional result payload.
            code (int, optional): Status code (default 200).

        Returns:
            ResultDTO: A success response object.
        """
        return ResultDTO(success=True, message=message, data=data, code=code)

    @staticmethod
    def fail(message: str, code: int = 400, data: Any = None) -> "ResultDTO":
        """
        Create a failure result object.

        Args:
            message (str): Error or failure message.
            code (int, optional): Status code (default 400).
            data (Any, optional): Optional payload for additional context.

        Returns:
            ResultDTO: A failure response object.
        """
        return ResultDTO(success=False, message=message, data=data, code=code)

    # ------------------------------------------------------------------
    # Backward Compatibility Aliases
    # ------------------------------------------------------------------
    success_ = ok
    error = fail

    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        """
        Convert the ResultDTO instance into a plain dictionary.

        Returns:
            dict[str, Any]: Dictionary representation of the result object.
        """
        return asdict(self)

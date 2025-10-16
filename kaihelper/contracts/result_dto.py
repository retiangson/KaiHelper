from dataclasses import dataclass, asdict
from typing import Any, Optional

@dataclass
class ResultDTO:
    success: bool
    message: str
    data: Optional[Any] = None
    code: Optional[int] = None

    # new safe names
    @staticmethod
    def ok(message: str, data: Any = None, code: int = 200) -> "ResultDTO":
        return ResultDTO(success=True, message=message, data=data, code=code)

    @staticmethod
    def fail(message: str, code: int = 400, data: Any = None) -> "ResultDTO":
        return ResultDTO(success=False, message=message, data=data, code=code)

    # optional backward-compatibility aliases
    success_ = ok
    error = fail

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

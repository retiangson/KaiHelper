"""
contracts/user_dto.py
Data Transfer Objects (DTOs) for User-related operations in KaiHelper.

These classes define how data flows between:
- UI Layer (Tkinter forms)
- Service Layer (business logic)
- Repository Layer (ORM persistence)
- Future API endpoints
"""

from dataclasses import dataclass


# ----------- Response / Output DTOs ----------- #
@dataclass
class UserDTO:
    """User details returned to the UI or API."""
    user_id: int
    name: str
    email: str
    email_verified: bool


# ----------- Input DTOs ----------- #
@dataclass
class RegisterUserDTO:
    """Data for user registration."""
    name: str
    email: str
    password: str


@dataclass
class LoginRequestDTO:
    """Login request payload."""
    email: str
    password: str


@dataclass
class LoginResponseDTO:
    """Response payload after successful login."""
    user_id: int
    name: str
    email: str
    message: str

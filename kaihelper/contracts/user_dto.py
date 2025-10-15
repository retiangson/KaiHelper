"""
User-related DTOs
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# A public view of a user (no password exposed externally)
@dataclass
class UserDTO:
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    id: Optional[int] = None
    password: Optional[str] = None  # internal use only


# Register payload
@dataclass
class RegisterUserDTO:
    username: str
    email: str
    full_name: Optional[str]
    password: str
    confirm_password: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


# Login payload (username or email + password)
@dataclass
class LoginRequestDTO:
    username_or_email: str
    password: str


# Profile response
@dataclass
class UserProfileDTO:
    username: str
    full_name: Optional[str]
    email: str
    created_at: datetime

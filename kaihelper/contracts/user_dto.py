"""
User-related DTOs
Data Transfer Objects used for user management operations.
"""

# --- Standard library imports ---
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class UserDTO:
    """
    Represents a public view of a user record.

    Attributes:
        id (int | None): Unique identifier for the user.
        username (str): User's username.
        email (str): User's email address.
        full_name (str | None): Optional user's full name.
        is_active (bool): Indicates whether the user account is active.
        created_at (datetime): Timestamp when the user was created.
        updated_at (datetime): Timestamp when the user was last updated.
        password (str | None): Optional internal field for password (not exposed externally).
    """
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    password: Optional[str] = None


@dataclass
class RegisterUserDTO:
    """
    Represents registration data submitted when creating a new account.

    Attributes:
        username (str): Desired username for the new user.
        email (str): User's email address.
        full_name (str | None): Optional full name of the user.
        password (str): Password for authentication.
        confirm_password (str): Password confirmation to ensure match.
        is_active (bool): Defaults to True upon registration.
        created_at (datetime): Timestamp when the user is created.
    """
    username: str
    email: str
    full_name: Optional[str] = None
    password: str = ""
    confirm_password: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class LoginRequestDTO:
    """
    Represents the credentials provided during user login.

    Attributes:
        username_or_email (str): Username or email for authentication.
        password (str): Password for login verification.
    """
    username_or_email: str
    password: str


@dataclass
class UserProfileDTO:
    """
    Represents a simplified user profile returned by the API.

    Attributes:
        username (str): Username of the user.
        full_name (str | None): Optional user's full name.
        email (str): Email address of the user.
        created_at (datetime): Account creation timestamp.
    """
    username: str
    full_name: Optional[str] = None
    email: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

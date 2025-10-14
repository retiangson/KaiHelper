"""
Utils Module
------------
Contains common utilities for hashing, verification, and other helpers.
"""

import bcrypt


def hash_password(plain_password: str) -> str:
    """Hashes a plain password using bcrypt."""
    if not plain_password:
        return ""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its bcrypt hash."""
    if not plain_password or not hashed_password:
        return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

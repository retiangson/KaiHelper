"""
User Repository (SQLAlchemy)
- Hashes passwords (bcrypt)
- Enforces unique email/username
"""
from typing import Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from kaihelper.domain.mappers.user_mapper import UserMapper

from kaihelper.domain.interfaces.i_user_repository import IUserRepository
from kaihelper.contracts.user_dto import RegisterUserDTO, UserDTO
from kaihelper.contracts.result_dto import ResultDTO
from kaihelper.domain.core.database import SessionLocal
from kaihelper.domain.models.user import User
from passlib.hash import pbkdf2_sha256

class UserRepository(IUserRepository):
    def __init__(self) -> None:
        self._SessionFactory = SessionLocal

    # ---------- helpers ----------
    def _to_public_dict(self, u: User) -> Dict[str, Any]:
        return {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "is_active": u.is_active,
            "created_at": u.created_at,
            "updated_at": u.updated_at,
        }

    # ---------- CRUD ----------
    def create_user(self, dto: RegisterUserDTO) -> ResultDTO:
        session: Session = self._SessionFactory()

        try:           
            new_user = UserMapper.to_entity(dto)

            session.add(new_user)
            session.commit()
            session.refresh(new_user)

            return ResultDTO(True, "User registered successfully", data=self._to_public_dict(new_user))
        except IntegrityError as ie:
            session.rollback()
            msg = str(getattr(ie, "orig", ie)).lower()
            if "email" in msg:
                return ResultDTO(False, f"Email '{dto.email}' already exists.")
            if "username" in msg:
                return ResultDTO(False, f"Username '{dto.username}' already exists.")
            return ResultDTO(False, "Unique constraint violated.")
        except Exception as e:
            session.rollback()
            return ResultDTO(False, f"Failed to register user: {e}")
        finally:
            session.close()

    def get_user_by_email(self, email: str) -> Optional[dict]:
        session: Session = self._SessionFactory()
        try:
            user = session.query(User).filter(User.email == email).first()
            return self._to_public_dict(user) if user else None
        finally:
            session.close()

    def get_user_by_id(self, user_id: int) -> Optional[dict]:
        session: Session = self._SessionFactory()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            return self._to_public_dict(user) if user else None
        finally:
            session.close()
            
    def get_username_or_email(self, username_or_email: str, password: str) -> UserDTO | None:
        session: Session = self._SessionFactory()
        try:
            if (q := session.query(User)
                    .filter((User.email == username_or_email) | (User.username == username_or_email))
                    .first()) is not None:
                return q if pbkdf2_sha256.verify(password, q.password) else None
            else:
                return None
        finally:
            session.close()

    # Auth helper for login
    def verify_credentials(self, username_or_email: str, password: str) -> Optional[dict]:
        session: Session = self._SessionFactory()
        try:
            if (q := session.query(User)
                    .filter((User.email == username_or_email) | (User.username == username_or_email))
                    .first()) is not None:
                return q if pbkdf2_sha256.verify(password, q.password) else None
            else:
                return None
        finally:
            session.close()

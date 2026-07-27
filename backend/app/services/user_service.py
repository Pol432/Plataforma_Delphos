"""
User Service - Persists ALL optional fields from UserCreate
"""
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.user_repository import UserRepository
from app.core.security import pwd_context


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def validate_new_user(self, user_data: UserCreate) -> None:
        if self.repository.email_exists(user_data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        if self.repository.username_exists(user_data.username):
            raise HTTPException(status_code=400, detail="Username already taken")

    def create_user(self, user_data: UserCreate) -> User:
        """Create user - Persists ALL fields including optionals"""
        self.validate_new_user(user_data)
        hashed_password = self.hash_password(user_data.password)

        # CRITICAL FIX: Use model_dump() to capture ALL fields
        user_dict = user_data.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        
        # Set defaults for model-required fields not in UserCreate
        user_dict.setdefault("xp_total", 0)
        user_dict.setdefault("level_current", 1)
        user_dict.setdefault("is_active", True)

        db_user = User(**user_dict)
        self.repository.db.add(db_user)
        self.repository.db.commit()
        self.repository.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.repository.get(user_id)

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.repository.get_by_username(username)
        if not user:
            user = self.repository.get_by_email(username)

        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

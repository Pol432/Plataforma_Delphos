"""
User Repository
Specific database operations for User model
"""
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    User-specific repository
    Extends BaseRepository with custom queries
    """
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email
        
        Args:
            email: User email
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get user by username
        
        Args:
            username: Username
            
        Returns:
            User instance or None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email is already registered
        
        Args:
            email: Email to check
            
        Returns:
            True if exists
        """
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def username_exists(self, username: str) -> bool:
        """
        Check if username is taken
        
        Args:
            username: Username to check
            
        Returns:
            True if exists
        """
        return self.db.query(User).filter(User.username == username).first() is not None
    
    def get_active_users(self, skip: int = 0, limit: int = 100):
        """
        Get only active users
        
        Args:
            skip: Pagination offset
            limit: Max records
            
        Returns:
            List of active users
        """
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()
    
    def get_by_xp_range(self, min_xp: int, max_xp: int):
        """
        Get users by XP range
        
        Args:
            min_xp: Minimum XP
            max_xp: Maximum XP
            
        Returns:
            List of users
        """
        return self.db.query(User).filter(
            User.xp_total >= min_xp,
            User.xp_total <= max_xp
        ).all()
    
    def get_by_level(self, level: int):
        """
        Get users by level
        
        Args:
            level: User level
            
        Returns:
            List of users
        """
        return self.db.query(User).filter(User.level_current == level).all()

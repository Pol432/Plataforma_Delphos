"""
API Dependencies
Centralized dependencies for FastAPI endpoints
"""
from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.db.session import get_db as _get_db
from app.models.user import User
from app.core.security import SECRET_KEY, ALGORITHM

# OAuth2 scheme configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


def get_db() -> Generator:
    """
    Database session dependency
    Yields a SQLAlchemy session and ensures proper cleanup
    """
    db = next(_get_db())
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token
    
    Args:
        token: JWT access token from Authorization header
        db: Database session
        
    Returns:
        User: Authenticated user instance
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current authenticated active user
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User: Active user instance
        
    Raises:
        HTTPException: 400 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

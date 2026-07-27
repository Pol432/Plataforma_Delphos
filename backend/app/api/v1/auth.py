"""
Authentication Router
Handles user registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserOut
from app.services.user_service import UserService
from app.core.security import create_access_token

router = APIRouter()


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login
    
    Authenticates user credentials and returns JWT access token
    
    Args:
        form_data: OAuth2 form with username and password
        db: Database session
        
    Returns:
        Token: Access token and token type
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    service = UserService(db)
    user = service.authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register new user
    
    Creates a new user account with hashed password
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        UserOut: Created user data (without password)
        
    Raises:
        HTTPException: 400 if email or username already exists
    """
    service = UserService(db)
    return service.create_user(user_data)


@router.get("/users/me", response_model=UserOut)
def read_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user profile
    
    Returns the profile of the currently logged-in user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserOut: Current user profile
    """
    return current_user

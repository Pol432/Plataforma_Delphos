"""
Users Router
Handles user CRUD operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.services.user_service import UserService

router = APIRouter()


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create new user (Admin/Public endpoint)
    
    Alternative registration endpoint (can be used for admin user creation)
    
    Args:
        user_data: User creation data
        db: Database session
        
    Returns:
        UserOut: Created user
        
    Raises:
        HTTPException: 400 if email/username exists
    """
    service = UserService(db)
    return service.create_user(user_data)


@router.get("", response_model=List[UserOut])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List all users (paginated)
    
    Requires authentication
    
    Args:
        skip: Number of records to skip
        limit: Maximum records to return
        db: Database session
        current_user: Authenticated user
        
    Returns:
        List[UserOut]: List of users
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/me", response_model=UserOut)
def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile
    
    Returns profile of authenticated user
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        UserOut: User profile
    """
    return current_user


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get user by ID
    
    Requires authentication
    
    Args:
        user_id: User ID to retrieve
        db: Database session
        current_user: Authenticated user
        
    Returns:
        UserOut: User data
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/me", response_model=UserOut)
@router.patch("/me", response_model=UserOut)
def update_my_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update current user profile
    
    Allows user to update their own profile
    
    Args:
        user_data: Fields to update
        db: Database session
        current_user: Authenticated user
        
    Returns:
        UserOut: Updated user profile
    """
    update_data = user_data.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(current_user, key, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.put("/{user_id}", response_model=UserOut)
@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update user by ID
    
    Users can only update their own profile
    
    Args:
        user_id: User ID to update
        user_data: Fields to update
        db: Database session
        current_user: Authenticated user
        
    Returns:
        UserOut: Updated user
        
    Raises:
        HTTPException: 404 if user not found, 403 if unauthorized
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Authorization check: users can only update their own profile
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete user by ID
    
    Users can only delete their own account
    
    Args:
        user_id: User ID to delete
        db: Database session
        current_user: Authenticated user
        
    Raises:
        HTTPException: 404 if user not found, 403 if unauthorized
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Authorization check: users can only delete their own account
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    db.delete(user)
    db.commit()
    return None

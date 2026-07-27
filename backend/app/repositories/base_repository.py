"""
Base Repository Pattern
Generic CRUD operations for all models
"""
from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository with CRUD operations
    
    Usage:
        class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
            pass
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def get(self, id: int) -> Optional[ModelType]:
        """
        Get single record by ID
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filters: dict = None
    ) -> List[ModelType]:
        """
        Get multiple records with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            filters: Optional filters dict
            
        Returns:
            List of model instances
        """
        query = self.db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.offset(skip).limit(limit).all()
    
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create new record
        
        Args:
            obj_in: Pydantic schema with data
            
        Returns:
            Created model instance
        """
        obj_in_data = obj_in.model_dump() if hasattr(obj_in, 'model_dump') else obj_in.dict()
        db_obj = self.model(**obj_in_data)
        
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        
        return db_obj
    
    def update(self, id: int, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """
        Update existing record
        
        Args:
            id: Record ID
            obj_in: Pydantic schema with update data
            
        Returns:
            Updated model instance or None
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True) if hasattr(obj_in, 'model_dump') else obj_in.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        self.db.commit()
        self.db.refresh(db_obj)
        
        return db_obj
    
    def delete(self, id: int) -> bool:
        """
        Delete record (hard delete)
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        db_obj = self.get(id)
        if not db_obj:
            return False
        
        self.db.delete(db_obj)
        self.db.commit()
        
        return True
    
    def soft_delete(self, id: int) -> Optional[ModelType]:
        """
        Soft delete (set is_active = False)
        
        Args:
            id: Record ID
            
        Returns:
            Deactivated model instance or None
        """
        db_obj = self.get(id)
        if not db_obj:
            return None
        
        if hasattr(db_obj, 'is_active'):
            db_obj.is_active = False
            self.db.commit()
            self.db.refresh(db_obj)
        
        return db_obj
    
    def count(self, filters: dict = None) -> int:
        """
        Count records
        
        Args:
            filters: Optional filters dict
            
        Returns:
            Total count
        """
        query = self.db.query(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.filter(getattr(self.model, key) == value)
        
        return query.count()
    
    def exists(self, id: int) -> bool:
        """
        Check if record exists
        
        Args:
            id: Record ID
            
        Returns:
            True if exists
        """
        return self.db.query(self.model).filter(self.model.id == id).first() is not None

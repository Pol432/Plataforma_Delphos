from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models import catalog as models
from app.schemas import catalog as schemas

router = APIRouter()

@router.get("/categories", response_model=List[schemas.ContentCategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.ContentCategory).all()

@router.get("/industries", response_model=List[schemas.IndustryOut])
def list_industries(db: Session = Depends(get_db)):
    return db.query(models.Industry).all()

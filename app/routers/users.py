from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from uuid import uuid4
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=list[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_users(db)


@router.post("/", response_model=schemas.UserRead)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    if db is None:
        return schemas.UserRead(id=str(uuid4()), created_at=datetime.utcnow(), **payload.model_dump())
    return crud.create_user(db, payload)

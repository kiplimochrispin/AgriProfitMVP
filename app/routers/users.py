from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_auth
from uuid import uuid4
from datetime import datetime

router = APIRouter()


@router.get("/", response_model=list[schemas.UserRead])
def list_users(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_users(db)


@router.post("/", response_model=schemas.UserRead)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    if db is None:
        return schemas.UserRead(id=str(uuid4()), created_at=datetime.utcnow(), **payload.model_dump())
    return crud.create_user(db, payload)


@router.patch("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: str,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    user = crud.update_user(db, user_id, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"status": "deleted"}

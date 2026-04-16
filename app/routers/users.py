from uuid import uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_auth, require_role

router = APIRouter()


@router.get("/", response_model=list[schemas.UserRead])
def list_users(
    db: Session = Depends(get_db),
    _: schemas.AuthUserRead = Depends(require_role("admin", "manager")),
):
    if db is None:
        return []
    return crud.get_users(db)


@router.post("/", response_model=schemas.UserRead)
def create_user(
    payload: schemas.UserCreate,
    db: Session = Depends(get_db),
    actor=Depends(require_role("admin")),
):
    if db is None:
        preview = payload.model_dump(exclude={"password"})
        return schemas.UserRead(id=str(uuid4()), created_at=datetime.now(timezone.utc), **preview)
    return crud.create_user(db, payload, actor=actor.username)


@router.patch("/{user_id}", response_model=schemas.UserRead)
def update_user(
    user_id: str,
    payload: schemas.UserUpdate,
    db: Session = Depends(get_db),
    actor=Depends(require_auth),
):
    if actor.role not in {"admin", "manager"} and actor.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    user = crud.update_user(db, user_id, payload, actor=actor.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    actor=Depends(require_role("admin")),
):
    deleted = crud.delete_user(db, user_id, actor=actor.username)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"status": "deleted"}

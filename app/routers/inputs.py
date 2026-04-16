from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_auth

router = APIRouter()


@router.get("/", response_model=list[schemas.InputUsageRead])
def list_inputs(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_input_usage(db)


@router.post("/", response_model=schemas.InputUsageRead)
def create_input(
    payload: schemas.InputUsageCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(require_auth),
):
    if db is None:
        return schemas.InputUsageRead(
            id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            **payload.model_dump(),
        )
    return crud.create_input_usage(db, payload, actor=actor.username)


@router.patch("/{input_id}", response_model=schemas.InputUsageRead)
def update_input(
    input_id: str,
    payload: schemas.InputUsageUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(require_auth),
):
    record = crud.update_input_usage(db, input_id, payload, actor=actor.username)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Input record not found")
    return record


@router.delete("/{input_id}")
def delete_input(
    input_id: str,
    db: Session = Depends(get_db),
    actor: str = Depends(require_auth),
):
    deleted = crud.delete_input_usage(db, input_id, actor=actor.username)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Input record not found")
    return {"status": "deleted"}

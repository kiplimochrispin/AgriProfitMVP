from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_auth

router = APIRouter()


@router.get("/", response_model=list[schemas.HarvestRecordRead])
def list_harvests(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_harvest_records(db)


@router.post("/", response_model=schemas.HarvestRecordRead)
def create_harvest(
    payload: schemas.HarvestRecordCreate,
    db: Session = Depends(get_db),
    actor: str = Depends(require_auth),
):
    if db is None:
        return schemas.HarvestRecordRead(
            id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
            **payload.model_dump(),
        )
    return crud.create_harvest_record(db, payload, actor=actor.username)


@router.patch("/{harvest_id}", response_model=schemas.HarvestRecordRead)
def update_harvest(
    harvest_id: str,
    payload: schemas.HarvestRecordUpdate,
    db: Session = Depends(get_db),
    actor: str = Depends(require_auth),
):
    record = crud.update_harvest_record(db, harvest_id, payload, actor=actor.username)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest record not found")
    return record


@router.delete("/{harvest_id}")
def delete_harvest(
    harvest_id: str,
    db: Session = Depends(get_db),
    actor: str = Depends(require_auth),
):
    deleted = crud.delete_harvest_record(db, harvest_id, actor=actor.username)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Harvest record not found")
    return {"status": "deleted"}

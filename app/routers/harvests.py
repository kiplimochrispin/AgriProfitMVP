from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.HarvestRecordRead])
def list_harvests(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_harvest_records(db)


@router.post("/", response_model=schemas.HarvestRecordRead)
def create_harvest(payload: schemas.HarvestRecordCreate, db: Session = Depends(get_db)):
    if db is None:
        return schemas.HarvestRecordRead(
            id=str(uuid4()),
            created_at=datetime.utcnow(),
            **payload.model_dump(),
        )
    return crud.create_harvest_record(db, payload)

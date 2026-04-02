from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.InputUsageRead])
def list_inputs(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_input_usage(db)


@router.post("/", response_model=schemas.InputUsageRead)
def create_input(payload: schemas.InputUsageCreate, db: Session = Depends(get_db)):
    if db is None:
        return schemas.InputUsageRead(
            id=str(uuid4()),
            created_at=datetime.utcnow(),
            **payload.model_dump(),
        )
    return crud.create_input_usage(db, payload)

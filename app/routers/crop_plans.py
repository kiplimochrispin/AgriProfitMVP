from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/", response_model=list[schemas.CropPlanRead])
def list_crop_plans(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_crop_plans(db)


@router.post("/", response_model=schemas.CropPlanRead)
def create_crop_plan(payload: schemas.CropPlanCreate, db: Session = Depends(get_db)):
    if db is None:
        return schemas.CropPlanRead(
            id=str(uuid4()),
            created_at=datetime.utcnow(),
            **payload.model_dump(),
        )
    return crud.create_crop_plan(db, payload)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from app import crud, schemas
from app.database import get_db
from app.security import require_auth

router = APIRouter()


@router.get("/", response_model=list[schemas.CropPlanRead])
def list_crop_plans(db: Session = Depends(get_db)):
    if db is None:
        return []
    return crud.get_crop_plans(db)


@router.post("/", response_model=schemas.CropPlanRead)
def create_crop_plan(
    payload: schemas.CropPlanCreate,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    if db is None:
        return schemas.CropPlanRead(
            id=str(uuid4()),
            created_at=datetime.utcnow(),
            **payload.model_dump(),
        )
    return crud.create_crop_plan(db, payload)


@router.patch("/{crop_plan_id}", response_model=schemas.CropPlanRead)
def update_crop_plan(
    crop_plan_id: str,
    payload: schemas.CropPlanUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    crop_plan = crud.update_crop_plan(db, crop_plan_id, payload)
    if crop_plan is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop plan not found")
    return crop_plan


@router.delete("/{crop_plan_id}")
def delete_crop_plan(
    crop_plan_id: str,
    db: Session = Depends(get_db),
    _: str = Depends(require_auth),
):
    deleted = crud.delete_crop_plan(db, crop_plan_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop plan not found")
    return {"status": "deleted"}

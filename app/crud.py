from sqlalchemy.orm import Session

from app import models, schemas


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).order_by(models.User.id.asc()).all()


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    user = models.User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_crop_plans(db: Session) -> list[models.CropPlan]:
    return db.query(models.CropPlan).order_by(models.CropPlan.id.asc()).all()


def create_crop_plan(db: Session, payload: schemas.CropPlanCreate) -> models.CropPlan:
    crop_plan = models.CropPlan(**payload.model_dump())
    db.add(crop_plan)
    db.commit()
    db.refresh(crop_plan)
    return crop_plan


def get_input_usage(db: Session) -> list[models.InputUsage]:
    return db.query(models.InputUsage).order_by(models.InputUsage.created_at.desc()).all()


def create_input_usage(db: Session, payload: schemas.InputUsageCreate) -> models.InputUsage:
    record = models.InputUsage(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_harvest_records(db: Session) -> list[models.HarvestRecord]:
    return db.query(models.HarvestRecord).order_by(models.HarvestRecord.created_at.desc()).all()


def create_harvest_record(db: Session, payload: schemas.HarvestRecordCreate) -> models.HarvestRecord:
    record = models.HarvestRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_fertilizer_recommendations(db: Session) -> list[models.FertilizerRecommendation]:
    return (
        db.query(models.FertilizerRecommendation)
        .order_by(
            models.FertilizerRecommendation.crop_type.asc(),
            models.FertilizerRecommendation.soil_type.asc(),
        )
        .all()
    )

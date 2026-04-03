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


def get_user(db: Session, user_id: str) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_user(db: Session, user_id: str, payload: schemas.UserUpdate) -> models.User | None:
    user = get_user(db, user_id)
    if user is None:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: str) -> bool:
    user = get_user(db, user_id)
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True


def get_crop_plans(db: Session) -> list[models.CropPlan]:
    return db.query(models.CropPlan).order_by(models.CropPlan.id.asc()).all()


def create_crop_plan(db: Session, payload: schemas.CropPlanCreate) -> models.CropPlan:
    crop_plan = models.CropPlan(**payload.model_dump())
    db.add(crop_plan)
    db.commit()
    db.refresh(crop_plan)
    return crop_plan


def get_crop_plan(db: Session, crop_plan_id: str) -> models.CropPlan | None:
    return db.query(models.CropPlan).filter(models.CropPlan.id == crop_plan_id).first()


def update_crop_plan(
    db: Session, crop_plan_id: str, payload: schemas.CropPlanUpdate
) -> models.CropPlan | None:
    crop_plan = get_crop_plan(db, crop_plan_id)
    if crop_plan is None:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(crop_plan, key, value)
    db.commit()
    db.refresh(crop_plan)
    return crop_plan


def delete_crop_plan(db: Session, crop_plan_id: str) -> bool:
    crop_plan = get_crop_plan(db, crop_plan_id)
    if crop_plan is None:
        return False
    db.delete(crop_plan)
    db.commit()
    return True


def get_input_usage(db: Session) -> list[models.InputUsage]:
    return db.query(models.InputUsage).order_by(models.InputUsage.created_at.desc()).all()


def create_input_usage(db: Session, payload: schemas.InputUsageCreate) -> models.InputUsage:
    record = models.InputUsage(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_input_record(db: Session, input_id: str) -> models.InputUsage | None:
    return db.query(models.InputUsage).filter(models.InputUsage.id == input_id).first()


def update_input_usage(
    db: Session, input_id: str, payload: schemas.InputUsageUpdate
) -> models.InputUsage | None:
    record = get_input_record(db, input_id)
    if record is None:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_input_usage(db: Session, input_id: str) -> bool:
    record = get_input_record(db, input_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def get_harvest_records(db: Session) -> list[models.HarvestRecord]:
    return db.query(models.HarvestRecord).order_by(models.HarvestRecord.created_at.desc()).all()


def create_harvest_record(db: Session, payload: schemas.HarvestRecordCreate) -> models.HarvestRecord:
    record = models.HarvestRecord(**payload.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_harvest_record(db: Session, harvest_id: str) -> models.HarvestRecord | None:
    return db.query(models.HarvestRecord).filter(models.HarvestRecord.id == harvest_id).first()


def update_harvest_record(
    db: Session, harvest_id: str, payload: schemas.HarvestRecordUpdate
) -> models.HarvestRecord | None:
    record = get_harvest_record(db, harvest_id)
    if record is None:
        return None
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    db.commit()
    db.refresh(record)
    return record


def delete_harvest_record(db: Session, harvest_id: str) -> bool:
    record = get_harvest_record(db, harvest_id)
    if record is None:
        return False
    db.delete(record)
    db.commit()
    return True


def get_fertilizer_recommendations(db: Session) -> list[models.FertilizerRecommendation]:
    return (
        db.query(models.FertilizerRecommendation)
        .order_by(
            models.FertilizerRecommendation.crop_type.asc(),
            models.FertilizerRecommendation.soil_type.asc(),
        )
        .all()
    )

import json

from sqlalchemy.orm import Session

from app import models, schemas
from app.security import hash_password


def create_audit_log(
    db: Session,
    *,
    actor: str | None,
    action: str,
    entity_type: str,
    entity_id: str,
    summary: str,
    payload: dict | None = None,
) -> models.AuditLog:
    audit_log = models.AuditLog(
        actor=actor or "system",
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        payload_json=json.dumps(payload, sort_keys=True) if payload is not None else None,
    )
    db.add(audit_log)
    return audit_log


def get_users(db: Session) -> list[models.User]:
    return db.query(models.User).order_by(models.User.id.asc()).all()


def create_user(db: Session, payload: schemas.UserCreate, actor: str | None = None) -> models.User:
    payload_data = payload.model_dump()
    password = payload_data.pop("password")
    user = models.User(**payload_data, password_hash=hash_password(password))
    db.add(user)
    db.flush()
    create_audit_log(
        db,
        actor=actor,
        action="create",
        entity_type="user",
        entity_id=user.id,
        summary=f"Created farmer {user.full_name or user.phone}",
        payload={**payload_data, "password": "***"},
    )
    db.commit()
    db.refresh(user)
    return user


def get_user(db: Session, user_id: str) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def update_user(db: Session, user_id: str, payload: schemas.UserUpdate, actor: str | None = None) -> models.User | None:
    user = get_user(db, user_id)
    if user is None:
        return None
    changes = payload.model_dump(exclude_unset=True)
    password = changes.pop("password", None)
    for key, value in changes.items():
        setattr(user, key, value)
    if password:
        user.password_hash = hash_password(password)
        changes["password"] = "***"
    create_audit_log(
        db,
        actor=actor,
        action="update",
        entity_type="user",
        entity_id=user.id,
        summary=f"Updated farmer {user.full_name or user.phone}",
        payload=changes,
    )
    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: str, actor: str | None = None) -> bool:
    user = get_user(db, user_id)
    if user is None:
        return False
    create_audit_log(
        db,
        actor=actor,
        action="delete",
        entity_type="user",
        entity_id=user.id,
        summary=f"Deleted farmer {user.full_name or user.phone}",
        payload={"phone": user.phone},
    )
    db.delete(user)
    db.commit()
    return True


def get_crop_plans(db: Session) -> list[models.CropPlan]:
    return db.query(models.CropPlan).order_by(models.CropPlan.id.asc()).all()


def create_crop_plan(db: Session, payload: schemas.CropPlanCreate, actor: str | None = None) -> models.CropPlan:
    crop_plan = models.CropPlan(**payload.model_dump())
    db.add(crop_plan)
    db.flush()
    create_audit_log(
        db,
        actor=actor,
        action="create",
        entity_type="crop_plan",
        entity_id=crop_plan.id,
        summary=f"Created crop plan for {crop_plan.crop_type}",
        payload=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(crop_plan)
    return crop_plan


def get_crop_plan(db: Session, crop_plan_id: str) -> models.CropPlan | None:
    return db.query(models.CropPlan).filter(models.CropPlan.id == crop_plan_id).first()


def update_crop_plan(
    db: Session, crop_plan_id: str, payload: schemas.CropPlanUpdate, actor: str | None = None
) -> models.CropPlan | None:
    crop_plan = get_crop_plan(db, crop_plan_id)
    if crop_plan is None:
        return None
    changes = payload.model_dump(exclude_unset=True, mode="json")
    for key, value in changes.items():
        setattr(crop_plan, key, value)
    create_audit_log(
        db,
        actor=actor,
        action="update",
        entity_type="crop_plan",
        entity_id=crop_plan.id,
        summary=f"Updated crop plan for {crop_plan.crop_type}",
        payload=changes,
    )
    db.commit()
    db.refresh(crop_plan)
    return crop_plan


def delete_crop_plan(db: Session, crop_plan_id: str, actor: str | None = None) -> bool:
    crop_plan = get_crop_plan(db, crop_plan_id)
    if crop_plan is None:
        return False
    create_audit_log(
        db,
        actor=actor,
        action="delete",
        entity_type="crop_plan",
        entity_id=crop_plan.id,
        summary=f"Deleted crop plan for {crop_plan.crop_type}",
        payload={"season_year": crop_plan.season_year},
    )
    db.delete(crop_plan)
    db.commit()
    return True


def get_input_usage(db: Session) -> list[models.InputUsage]:
    return db.query(models.InputUsage).order_by(models.InputUsage.created_at.desc()).all()


def create_input_usage(
    db: Session, payload: schemas.InputUsageCreate, actor: str | None = None
) -> models.InputUsage:
    record = models.InputUsage(**payload.model_dump())
    db.add(record)
    db.flush()
    create_audit_log(
        db,
        actor=actor,
        action="create",
        entity_type="input_usage",
        entity_id=record.id,
        summary=f"Created input {record.item_name}",
        payload=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(record)
    return record


def get_input_record(db: Session, input_id: str) -> models.InputUsage | None:
    return db.query(models.InputUsage).filter(models.InputUsage.id == input_id).first()


def update_input_usage(
    db: Session, input_id: str, payload: schemas.InputUsageUpdate, actor: str | None = None
) -> models.InputUsage | None:
    record = get_input_record(db, input_id)
    if record is None:
        return None
    changes = payload.model_dump(exclude_unset=True, mode="json")
    for key, value in changes.items():
        setattr(record, key, value)
    create_audit_log(
        db,
        actor=actor,
        action="update",
        entity_type="input_usage",
        entity_id=record.id,
        summary=f"Updated input {record.item_name}",
        payload=changes,
    )
    db.commit()
    db.refresh(record)
    return record


def delete_input_usage(db: Session, input_id: str, actor: str | None = None) -> bool:
    record = get_input_record(db, input_id)
    if record is None:
        return False
    create_audit_log(
        db,
        actor=actor,
        action="delete",
        entity_type="input_usage",
        entity_id=record.id,
        summary=f"Deleted input {record.item_name}",
        payload={"category": record.category},
    )
    db.delete(record)
    db.commit()
    return True


def get_harvest_records(db: Session) -> list[models.HarvestRecord]:
    return db.query(models.HarvestRecord).order_by(models.HarvestRecord.created_at.desc()).all()


def create_harvest_record(
    db: Session, payload: schemas.HarvestRecordCreate, actor: str | None = None
) -> models.HarvestRecord:
    record = models.HarvestRecord(**payload.model_dump())
    db.add(record)
    db.flush()
    create_audit_log(
        db,
        actor=actor,
        action="create",
        entity_type="harvest_record",
        entity_id=record.id,
        summary="Created harvest record",
        payload=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(record)
    return record


def get_harvest_record(db: Session, harvest_id: str) -> models.HarvestRecord | None:
    return db.query(models.HarvestRecord).filter(models.HarvestRecord.id == harvest_id).first()


def update_harvest_record(
    db: Session, harvest_id: str, payload: schemas.HarvestRecordUpdate, actor: str | None = None
) -> models.HarvestRecord | None:
    record = get_harvest_record(db, harvest_id)
    if record is None:
        return None
    changes = payload.model_dump(exclude_unset=True, mode="json")
    for key, value in changes.items():
        setattr(record, key, value)
    create_audit_log(
        db,
        actor=actor,
        action="update",
        entity_type="harvest_record",
        entity_id=record.id,
        summary="Updated harvest record",
        payload=changes,
    )
    db.commit()
    db.refresh(record)
    return record


def delete_harvest_record(db: Session, harvest_id: str, actor: str | None = None) -> bool:
    record = get_harvest_record(db, harvest_id)
    if record is None:
        return False
    create_audit_log(
        db,
        actor=actor,
        action="delete",
        entity_type="harvest_record",
        entity_id=record.id,
        summary="Deleted harvest record",
        payload={"crop_plan_id": record.crop_plan_id},
    )
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


def get_audit_logs(db: Session, limit: int = 50) -> list[models.AuditLog]:
    return db.query(models.AuditLog).order_by(models.AuditLog.created_at.desc()).limit(limit).all()

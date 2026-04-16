from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.security import require_role

router = APIRouter()


@router.get("/", response_model=list[schemas.AuditLogRead])
def list_audit_logs(
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: schemas.AuthUserRead = Depends(require_role("admin", "manager")),
):
    if db is None:
        return []
    return crud.get_audit_logs(db, limit=limit)

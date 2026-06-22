from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/logs", tags=["Logs"])

@router.get("/", response_model=List[schemas.DeliveryLogResponse])
def read_logs(
    endpoint_id: Optional[UUID] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(models.DeliveryLog)
    if endpoint_id:
        query = query.filter(models.DeliveryLog.endpoint_id == endpoint_id)
    if status:
        query = query.filter(models.DeliveryLog.status == status)
    
    return query.order_by(models.DeliveryLog.created_at.desc()).offset(skip).limit(limit).all()

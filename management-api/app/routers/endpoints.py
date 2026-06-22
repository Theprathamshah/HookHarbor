import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from ..database import get_db
from .. import models, schemas

router = APIRouter(prefix="/endpoints", tags=["Endpoints"])

@router.post("/", response_model=schemas.EndpointResponse, status_code=status.HTTP_201_CREATED)
def create_endpoint(endpoint: schemas.EndpointCreate, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(models.User).filter(models.User.id == endpoint.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate signing secret (e.g. whsec_...)
    secret = "whsec_" + secrets.token_hex(24)

    db_endpoint = models.Endpoint(
        user_id=endpoint.user_id,
        name=endpoint.name,
        target_url=endpoint.target_url,
        secret=secret,
        max_retries=endpoint.max_retries,
        active=endpoint.active
    )
    db.add(db_endpoint)
    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint

@router.get("/", response_model=List[schemas.EndpointResponse])
def read_endpoints(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(models.Endpoint).offset(skip).limit(limit).all()

@router.get("/{endpoint_id}", response_model=schemas.EndpointResponse)
def read_endpoint(endpoint_id: UUID, db: Session = Depends(get_db)):
    db_endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    return db_endpoint

@router.put("/{endpoint_id}", response_model=schemas.EndpointResponse)
def update_endpoint(endpoint_id: UUID, endpoint_update: schemas.EndpointUpdate, db: Session = Depends(get_db)):
    db_endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    
    update_data = endpoint_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_endpoint, key, value)

    db.commit()
    db.refresh(db_endpoint)
    return db_endpoint

@router.delete("/{endpoint_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(endpoint_id: UUID, db: Session = Depends(get_db)):
    db_endpoint = db.query(models.Endpoint).filter(models.Endpoint.id == endpoint_id).first()
    if not db_endpoint:
        raise HTTPException(status_code=404, detail="Endpoint not found")
    db.delete(db_endpoint)
    db.commit()
    return

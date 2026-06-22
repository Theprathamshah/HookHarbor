from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional, Dict, Any

# User Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True

# Endpoint Schemas
class EndpointBase(BaseModel):
    name: str
    target_url: str
    max_retries: int = 5
    active: bool = True

class EndpointCreate(EndpointBase):
    user_id: UUID

class EndpointUpdate(BaseModel):
    name: Optional[str] = None
    target_url: Optional[str] = None
    max_retries: Optional[int] = None
    active: Optional[bool] = None

class EndpointResponse(EndpointBase):
    id: UUID
    user_id: UUID
    secret: str
    created_at: datetime

    class Config:
        from_attributes = True

# DeliveryLog Schemas
class DeliveryLogResponse(BaseModel):
    id: UUID
    endpoint_id: UUID
    request_payload: str
    request_headers: Dict[str, Any]
    response_code: Optional[int]
    response_body: Optional[str]
    status: str
    attempt_number: int
    duration_ms: int
    created_at: datetime

    class Config:
        from_attributes = True

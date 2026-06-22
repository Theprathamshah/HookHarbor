import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    api_key = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    endpoints = relationship("Endpoint", back_populates="user", cascade="all, delete-orphan")

class Endpoint(Base):
    __tablename__ = "endpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    target_url = Column(Text, nullable=False)
    secret = Column(String(128), nullable=False)
    max_retries = Column(Integer, default=5, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="endpoints")
    logs = relationship("DeliveryLog", back_populates="endpoint", cascade="all, delete-orphan")

class DeliveryLog(Base):
    __tablename__ = "delivery_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint_id = Column(UUID(as_uuid=True), ForeignKey("endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    request_payload = Column(Text, nullable=False)
    request_headers = Column(JSONB, nullable=False)
    response_code = Column(Integer, nullable=True)
    response_body = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, index=True) # SUCCESS, FAILED, RETRYING
    attempt_number = Column(Integer, default=1, nullable=False)
    duration_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    endpoint = relationship("Endpoint", back_populates="logs")

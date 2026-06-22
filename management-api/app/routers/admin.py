import secrets
import pika
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from ..config import settings

router = APIRouter(prefix="/admin", tags=["Admin & DLQ"])

@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate API key
    api_key = "hk_" + secrets.token_urlsafe(32)
    new_user = models.User(email=user.email, api_key=api_key)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/dlq/replay")
def replay_dlq():
    """
    Manually read all messages from DLQ and push them back into the main jobs queue.
    """
    try:
        parameters = pika.URLParameters(settings.RABBITMQ_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        replayed_count = 0
        while True:
            # Get message from DLQ without auto-ack
            method_frame, header_frame, body = channel.basic_get(queue="webhook.dlq", auto_ack=False)
            if not method_frame:
                break
            
            # Publish back to main jobs exchange
            channel.basic_publish(
                exchange="webhook.directExchange",
                routing_key="jobs",
                body=body,
                properties=pika.BasicProperties(delivery_mode=2) # Persistent
            )
            
            # Acknowledge DLQ message after successful forward
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
            replayed_count += 1
            
        connection.close()
        return {"status": "success", "replayed_messages": replayed_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to replay DLQ: {str(e)}")

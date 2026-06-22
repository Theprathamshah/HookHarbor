import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hookharbor")
    RABBITMQ_URL: str = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "hookharbor_admin_secret_key")

settings = Settings()

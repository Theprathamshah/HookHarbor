from fastapi import FastAPI
from .routers import endpoints, logs, admin
from .database import engine, Base

# Auto-create tables (for local dev; migrations are handled in db/migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HookHarbor Management API",
    description="Control plane for managing Webhook endpoints, logs, and DLQ retries.",
    version="1.0.0"
)

# Register routers
app.include_router(endpoints.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "service": "HookHarbor Management API",
        "status": "online",
        "docs": "/docs"
    }

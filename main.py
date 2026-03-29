# main.py
from fastapi import FastAPI
from src.core.config import settings
from src.db.database import engine
from src.db.base import Base
from src.models import trade  # noqa: F401
from src.api.routes import trades

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered trading research and decision support assistant.",
)

# Register route modules
app.include_router(trades.router)


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")


@app.get("/")
def root():
    return {"message": "AI Trading Agent API is running."}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "environment": settings.environment,
        "app": settings.app_name,
    }

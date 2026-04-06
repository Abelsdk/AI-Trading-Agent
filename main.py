# main.py
from fastapi import FastAPI
from src.core.config import settings
from src.db.database import engine
from src.db.base import Base
from src.models import trade, price_bar  # noqa: F401
from src.api.routes import trades, market_data, analytics, ai

app = FastAPI(
    title=settings.app_name,
    version="0.3.0",
    description="AI-powered trading research and decision support assistant.",
)

app.include_router(trades.router)
app.include_router(market_data.router)
app.include_router(analytics.router)
app.include_router(ai.router)


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
        "version": "0.3.0",
    }
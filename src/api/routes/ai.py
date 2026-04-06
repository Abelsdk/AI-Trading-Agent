# src/api/routes/ai.py
# HTTP endpoints for the AI reasoning layer.

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.db.database import get_db
from src.services import ai_service

router = APIRouter(
    prefix="/api/v1/ai",
    tags=["ai insights"],
)


@router.get("/analyze-trade/{trade_id}")
def analyze_trade(
    trade_id: int,
    db: Session = Depends(get_db),
):
    """
    Generate AI post-mortem analysis for a closed trade.
    Explains what worked, what didn't, and key lessons.
    """
    return ai_service.analyze_trade(db, trade_id)


@router.get("/analyze-journal")
def analyze_journal(db: Session = Depends(get_db)):
    """
    Analyze patterns across all closed trades.
    Identifies behavioral patterns and generates insights.
    """
    return ai_service.analyze_journal_patterns(db)


@router.get("/ask")
def ask_question(
    question: str = Query(..., description="Ask anything about trading"),
):
    """
    Free-form trading Q&A powered by local LLM.
    Ask about strategies, risk management, market concepts.
    """
    return ai_service.ask_trading_question(question)
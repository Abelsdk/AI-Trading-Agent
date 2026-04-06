# src/services/ai_service.py
# AI reasoning layer using local Ollama LLM.
# This service takes structured trade data computed by Python,
# formats it into a prompt, and asks the LLM to reason about it.
# The LLM never computes numbers — Python does that. The LLM explains.

import ollama
from sqlalchemy.orm import Session
from typing import Optional
from src.models.trade import Trade, TradeStatus, TradeDirection
from src.services.analytics_service import (
    calculate_trade_pnl,
    calculate_r_multiple,
    get_performance_summary,
)

# The model we're using — change this one line to switch models
OLLAMA_MODEL = "llama3.2:3b"

# System prompt — defines the AI's role and constraints
SYSTEM_PROMPT = """You are a sharp, experienced trader helping a student develop 
real trading skills. You are direct, concise, and strategic.

Your style:
- No fluff, no backstory, no preamble
- Get straight to the point
- Think like a professional trader, not a cautious teacher
- Be honest about what actually works vs what sounds good in theory
- Acknowledge risk without being preachy about it
- Treat the student as intelligent and capable
- Give answers that a profitable trader would actually use

Never start with "As a trading coach" or similar phrases.
Never repeat the question back.
Just answer directly and precisely."""


def analyze_trade(db: Session, trade_id: int) -> dict:
    """
    Generate an AI post-mortem analysis for a single closed trade.
    Computes all statistics in Python first, then asks LLM to explain.
    """
    # Fetch the trade
    trade = db.query(Trade).filter(Trade.id == trade_id).first()
    if not trade:
        return {"error": f"Trade {trade_id} not found"}

    if trade.status != TradeStatus.CLOSED:
        return {"error": "Trade must be closed before analysis"}

    # Compute statistics in Python — never delegate math to LLM
    pnl = calculate_trade_pnl(trade)
    r_multiple = calculate_r_multiple(trade)
    
    pnl_str = f"${pnl:.2f}" if pnl else "unknown"
    r_str = f"{r_multiple:.2f}R" if r_multiple else "unknown"
    direction = trade.direction.value if trade.direction else "unknown"
    
    # Calculate hold duration
    duration = None
    if trade.entry_time and trade.exit_time:
        delta = trade.exit_time - trade.entry_time
        duration = f"{delta.days}d {delta.seconds // 3600}h"

    # Build structured context for the LLM
    # The more context we provide, the better the analysis
    stop_loss_str = f"${float(trade.stop_loss):.4f}" if trade.stop_loss else "not set"
    take_profit_str = f"${float(trade.take_profit):.4f}" if trade.take_profit else "not set"
    risk_str = f"{float(trade.risk_percent):.1f}%" if trade.risk_percent else "not set"
    entry_str = f"${float(trade.entry_price):.4f}"
    exit_str = f"${float(trade.exit_price):.4f}"

    user_prompt = f"""Please analyze this trade for educational insights:

TRADE DETAILS:
- Symbol: {trade.symbol}
- Direction: {direction}
- Entry Price: {entry_str}
- Exit Price: {exit_str}
- Quantity: {float(trade.quantity)}
- Hold Duration: {duration or 'unknown'}

RISK MANAGEMENT:
- Stop Loss: {stop_loss_str}
- Take Profit: {take_profit_str}
- Risk Percent: {risk_str}

OUTCOME:
- P&L: {pnl_str}
- R-Multiple: {r_str}
- Result: {'Profit' if pnl and pnl > 0 else 'Loss'}

TRADER CONTEXT:
- Strategy Used: {trade.strategy or 'not tagged'}
- Reasoning at Entry: {trade.reasoning or 'not recorded'}
- Emotional State: {trade.emotion or 'not recorded'}
- Post-Trade Notes: {trade.notes or 'none'}

Please provide:
1. What went well in this trade
2. What could be improved
3. One key lesson to remember
4. A risk management observation

Keep your response concise and educational."""

    # Call the local Ollama model
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        
        analysis_text = response["message"]["content"]
        
        return {
            "trade_id": trade_id,
            "symbol": trade.symbol,
            "pnl": pnl,
            "r_multiple": r_multiple,
            "analysis": analysis_text,
            "model": OLLAMA_MODEL,
        }
        
    except Exception as e:
        return {
            "error": f"AI analysis failed: {str(e)}",
            "hint": "Make sure Ollama is running: ollama serve &"
        }


def analyze_journal_patterns(db: Session) -> dict:
    """
    Analyze patterns across all closed trades.
    Identifies behavioral patterns, best/worst conditions,
    and generates hypotheses about what works.
    """
    # Get performance summary computed by Python
    summary = get_performance_summary(db)
    
    if summary.get("status") == "no_data":
        return {"error": "No closed trades to analyze"}

    # Get recent trades for pattern context
    recent_trades = (
        db.query(Trade)
        .filter(Trade.status == TradeStatus.CLOSED)
        .order_by(Trade.entry_time.desc())
        .limit(20)
        .all()
    )

    # Build trade list for context
    trade_summaries = []
    for t in recent_trades:
        pnl = calculate_trade_pnl(t)
        r = calculate_r_multiple(t)
        trade_summaries.append(
            f"- {t.symbol} {t.direction.value}: "
            f"P&L={f'${pnl:.2f}' if pnl else 'N/A'}, "
            f"R={f'{r:.1f}R' if r else 'N/A'}, "
            f"Strategy={t.strategy or 'none'}, "
            f"Emotion={t.emotion or 'none'}"
        )

    trades_text = "\n".join(trade_summaries) if trade_summaries else "No trades"

    user_prompt = f"""Analyze these trading journal statistics and identify patterns:

OVERALL PERFORMANCE:
- Total Trades: {summary['total_trades']}
- Win Rate: {summary['win_rate']}%
- Total P&L: ${summary['total_pnl']}
- Average Win: ${summary['avg_win']}
- Average Loss: ${summary['avg_loss']}
- Expectancy: ${summary['expectancy']} per trade
- R-Expectancy: {summary.get('r_expectancy', 'N/A')}R
- Max Drawdown: ${summary['max_drawdown']}
- Profit Factor: {summary['profit_factor']}
- Max Win Streak: {summary['max_win_streak']}
- Max Loss Streak: {summary['max_loss_streak']}

RECENT TRADES:
{trades_text}

Please provide:
1. The most important pattern you notice
2. The biggest risk management concern
3. Which conditions seem to produce better results
4. One specific thing to focus on improving
5. An honest assessment of this trading performance

Be direct, educational, and honest. This student is learning."""

    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        return {
            "analysis": response["message"]["content"],
            "based_on_trades": summary["total_trades"],
            "model": OLLAMA_MODEL,
            "performance_summary": summary,
        }

    except Exception as e:
        return {
            "error": f"AI analysis failed: {str(e)}",
            "hint": "Make sure Ollama is running: ollama serve &"
        }


def ask_trading_question(question: str) -> dict:
    """
    Free-form Q&A about trading concepts.
    The student can ask anything about markets, strategies, or risk management.
    """
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
        )

        return {
            "question": question,
            "answer": response["message"]["content"],
            "model": OLLAMA_MODEL,
        }

    except Exception as e:
        return {
            "error": f"AI response failed: {str(e)}",
            "hint": "Make sure Ollama is running: ollama serve &"
        }
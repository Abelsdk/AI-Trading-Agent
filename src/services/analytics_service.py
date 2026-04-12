# src/services/analytics_service.py
# Computes trading performance metrics from the trade journal.
# All calculations are pure Python/math — no LLM involved.
# The AI layer later uses these numbers as context for explanations.

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
import math
from src.models.trade import Trade, TradeStatus, TradeDirection


def calculate_trade_pnl(trade: Trade) -> Optional[float]:
    """
    Calculate profit/loss for a single closed trade.
    LONG: profit when price goes up. SHORT: profit when price goes down.
    """
    if trade.exit_price is None or trade.entry_price is None:
        return None
    
    entry = float(trade.entry_price)
    exit_p = float(trade.exit_price)
    qty = float(trade.quantity)
    
    if trade.direction == TradeDirection.LONG:
        return (exit_p - entry) * qty
    else:
        return (entry - exit_p) * qty


def calculate_r_multiple(trade: Trade) -> Optional[float]:
    """
    R-multiple = profit expressed as a ratio of initial risk.
    Example: risked $100, made $250 = +2.5R
    This is more useful than raw P&L for comparing trades of different sizes.
    """
    if trade.stop_loss is None or trade.exit_price is None:
        return None
    
    entry = float(trade.entry_price)
    stop = float(trade.stop_loss)
    exit_p = float(trade.exit_price)
    
    risk_per_unit = abs(entry - stop)
    if risk_per_unit == 0:
        return None
    
    if trade.direction == TradeDirection.LONG:
        return (exit_p - entry) / risk_per_unit
    else:
        return (entry - exit_p) / risk_per_unit


def get_performance_summary(
    db: Session,
    strategy: Optional[str] = None,
    symbol: Optional[str] = None,
) -> dict:
    """
    Compute full performance summary from closed trades.
    Optionally filter by strategy or symbol.
    
    Returns: win rate, expectancy, avg win/loss, max drawdown,
             Sharpe-like ratio, streak info, and per-strategy breakdown.
    """
    # Query only closed trades
    query = db.query(Trade).filter(Trade.status == TradeStatus.CLOSED)
    
    if strategy:
        query = query.filter(Trade.strategy == strategy)
    if symbol:
        query = query.filter(Trade.symbol == symbol.upper())
    
    trades = query.order_by(Trade.entry_time).all()
    
    if not trades:
        return {"status": "no_data", "message": "No closed trades found"}

    # Calculate P&L for each trade
    pnls = []
    r_multiples = []
    
    for trade in trades:
        pnl = calculate_trade_pnl(trade)
        if pnl is not None:
            pnls.append(pnl)
        
        r = calculate_r_multiple(trade)
        if r is not None:
            r_multiples.append(r)

    if not pnls:
        return {"status": "no_data", "message": "No trades with complete entry/exit data"}

    # Core metrics
    total_trades = len(pnls)
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    
    win_rate = len(wins) / total_trades if total_trades > 0 else 0
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = sum(losses) / len(losses) if losses else 0
    total_pnl = sum(pnls)
    
    # Expectancy = (win rate × avg win) + (loss rate × avg loss)
    # Positive expectancy = profitable system over many trades
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    
    # Profit factor = gross profit / gross loss
    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else 999.99
    
    # Max drawdown — largest peak-to-trough decline in cumulative P&L
    cumulative = []
    running = 0
    for p in pnls:
        running += p
        cumulative.append(running)
    
    max_drawdown = 0
    peak = cumulative[0]
    for value in cumulative:
        if value > peak:
            peak = value
        drawdown = peak - value
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    
    # Sharpe-like ratio (simplified — uses P&L not returns)
    if len(pnls) > 1:
        mean_pnl = sum(pnls) / len(pnls)
        variance = sum((p - mean_pnl) ** 2 for p in pnls) / len(pnls)
        std_dev = math.sqrt(variance)
        sharpe = (mean_pnl / std_dev) * math.sqrt(252) if std_dev > 0 else 0
    else:
        sharpe = 0
    
    # Win/loss streak
    current_streak = 1
    max_win_streak = 0
    max_loss_streak = 0
    
    for i in range(1, len(pnls)):
        if (pnls[i] > 0) == (pnls[i-1] > 0):
            current_streak += 1
        else:
            current_streak = 1
        
        if pnls[i] > 0:
            max_win_streak = max(max_win_streak, current_streak)
        else:
            max_loss_streak = max(max_loss_streak, current_streak)

    # R-multiple expectancy (more reliable metric)
    r_expectancy = sum(r_multiples) / len(r_multiples) if r_multiples else None

    return {
        "total_trades": total_trades,
        "win_rate": round(win_rate * 100, 2),
        "total_pnl": round(total_pnl, 2),
        "avg_win": round(avg_win, 2),
        "avg_loss": round(avg_loss, 2),
        "expectancy": round(expectancy, 2),
        "r_expectancy": round(r_expectancy, 3) if r_expectancy else None,
        "profit_factor": round(profit_factor, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe, 3),
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        "wins": len(wins),
        "losses": len(losses),
        "filters": {
            "strategy": strategy,
            "symbol": symbol,
        }
    }


def get_strategy_breakdown(db: Session) -> list[dict]:
    """Performance summary broken down by strategy tag."""
    strategies = (
        db.query(Trade.strategy)
        .filter(Trade.status == TradeStatus.CLOSED)
        .filter(Trade.strategy.isnot(None))
        .distinct()
        .all()
    )
    
    results = []
    for (strategy,) in strategies:
        summary = get_performance_summary(db, strategy=strategy)
        if summary.get("total_trades", 0) > 0:
            summary["strategy"] = strategy
            results.append(summary)
    
    return sorted(results, key=lambda x: x.get("expectancy", 0), reverse=True)
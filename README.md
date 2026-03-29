# AI Trading Agent

An AI-powered trading research and decision support platform built as a software engineering portfolio project.

## What it does
- Trading journal with full CRUD API
- Market data ingestion for stocks and crypto
- Technical indicator computation (RSI, MACD, MA, ATR)
- Analytics engine: win rate, expectancy, Sharpe ratio, drawdown
- AI-powered trade analysis via Claude API
- React dashboard with equity curves and performance metrics

## Tech Stack
- **Backend**: Python 3.12, FastAPI, SQLAlchemy, Alembic
- **Database**: PostgreSQL + TimescaleDB, Redis
- **AI**: Anthropic Claude API
- **Frontend**: React 18, TypeScript, TailwindCSS, Recharts
- **Infrastructure**: Docker, Docker Compose

## Status
- [x] Phase 1: Trading journal API (complete)
- [ ] Phase 2: Market data + analytics engine
- [ ] Phase 3: AI layer + React dashboard

## Setup
```bash
git clone https://github.com/Abelsdk/AI-Trading-Agent
cd AI-Trading-Agent
python3.12 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API.

---
*For educational purposes only. Not financial advice.*
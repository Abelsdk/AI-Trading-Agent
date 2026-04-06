# AI Trading Agent

An AI-powered trading research and decision support platform built as a 
software engineering portfolio project. Designed for learning markets through 
data, journaling trades, and AI-assisted pattern recognition.

> **Disclaimer:** This project is for educational purposes only. 
> Not financial advice. 
---

## What It Does

- **Trading Journal** — Log trades with full context: entry, exit, strategy, 
  reasoning, emotion, risk taken
- **Market Data** — Fetch and store real OHLCV price data for stocks and crypto 
  via Yahoo Finance (free, no API key)
- **Analytics Engine** — Compute win rate, expectancy, Sharpe ratio, max 
  drawdown, R-multiples, profit factor
- **AI Insights** — Claude API explains why trades worked or failed, detects 
  behavioral patterns, generates hypotheses
- **Dashboard** — React frontend with equity curves, performance metrics, 
  trade history, and AI insight panel

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12 |
| API Framework | FastAPI |
| Database | PostgreSQL 16 + TimescaleDB |
| ORM | SQLAlchemy 2.0 + Alembic |
| Data Validation | Pydantic v2 |
| Market Data | yfinance, pandas, pandas-ta |
| Cache / Queue | Redis 7 |
| AI Layer | Anthropic Claude API |
| Frontend | React 18, TypeScript, TailwindCSS |
| Infrastructure | Docker, Docker Compose |

---

## Project Status

| Phase | Description | Status |
|---|---|---|
| Phase 0 | Environment setup | Complete |
| Phase 1 | Trading journal API + database | Complete |
| Phase 2 | Market data ingestion + analytics engine | Complete |
| Phase 3 | AI layer + React dashboard | In progress |

---

## Prerequisites

Install these before anything else, in this order:

1. **Homebrew** (Mac) — [brew.sh](https://brew.sh)
2. **Python 3.12** — `brew install python@3.12`
3. **Node.js 20 LTS** — `brew install node@20`
4. **Git + GitHub CLI** — `brew install git gh`
5. **Docker Desktop** — `brew install --cask docker`

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Abelsdk/AI-Trading-Agent.git
cd AI-Trading-Agent
```

### 2. Create and activate virtual environment
```bash
/opt/homebrew/opt/python@3.12/bin/python3.12 -m venv venv
source venv/bin/activate
```

### 3. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 4. Create your environment file
```bash
cp .env.example .env
```
Then open `.env` and fill in your values.

### 5. Start the database and Redis
```bash
# Open Docker Desktop first, wait for whale icon in menu bar
docker compose up -d
```

### 6. Run database migrations
```bash
alembic upgrade head
```

### 7. Start the API server
```bash
uvicorn main:app --reload
```

### 8. Open the API docs
Visit [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Environment Variables

Create a `.env` file at the project root. Never commit this file.
```bash
# .env
DATABASE_URL=postgresql://marketmind:marketmind_dev@localhost:5432/marketmind
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
APP_NAME=AI Trading Agent
ANTHROPIC_API_KEY=your-claude-api-key-here   # Phase 3
```

A `.env.example` file is committed to the repo with placeholder values 
so new developers know what variables are required.

---

## Daily Development Workflow

### Starting a session
```bash
# 1. Open Docker Desktop — wait for whale icon in menu bar
# 2. Then in terminal:
cd /Users/abelsaddik/Developer/projects/ai-trading-agent
source venv/bin/activate
docker compose up -d
uvicorn main:app --reload
```

### Ending a session
```bash
# Ctrl+C to stop uvicorn
docker compose down
deactivate
# Quit Docker Desktop from menu bar
```

---

## API Endpoints

### Trading Journal
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/trades/` | Log a new trade |
| GET | `/api/v1/trades/` | List all trades (filterable) |
| GET | `/api/v1/trades/{id}` | Get single trade |
| PATCH | `/api/v1/trades/{id}` | Update / close a trade |
| DELETE | `/api/v1/trades/{id}` | Delete a trade |

### Market Data
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/market-data/fetch` | Fetch & store OHLCV from Yahoo Finance |
| GET | `/api/v1/market-data/prices/{symbol}` | Get stored price bars |
| GET | `/api/v1/market-data/symbols` | List symbols with stored data |

### Analytics
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/analytics/summary` | Full performance summary |
| GET | `/api/v1/analytics/strategies` | Performance by strategy |

---

## Project Structure
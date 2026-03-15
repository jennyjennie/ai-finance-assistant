# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI Financial Assistant — conversational MVP with real-time financial data. Backend uses Claude tool-calling agentic loop; frontend is a Next.js chat UI with a portfolio chart tab.

**Data sources:** yfinance (stocks), FRED API (CPI, interest rates)
**Model:** `claude-haiku-4-5-20251001`

## Architecture

```
ai-finance-assistant/
├── backend/
│   ├── main.py                 # FastAPI app; mounts /chat and portfolio router
│   ├── claude_client.py        # Agentic loop (max_tokens=8192), _SafeEncoder for NaN
│   ├── tool_definitions.py     # JSON Schema for all 6 tools
│   ├── models.py               # Pydantic: Message, ChatRequest, ChatResponse
│   ├── tools/
│   │   ├── stock.py            # get_stock_quote, get_financials, get_risk_metrics,
│   │   │                       # compare_stocks, get_portfolio_analysis
│   │   └── macro.py            # get_cpi, get_interest_rate (FRED)
│   └── routers/
│       └── portfolio.py        # POST /portfolio/history (chart data)
└── frontend/
    ├── app/
    │   ├── page.tsx            # Two tabs: Chat / Portfolio Chart
    │   ├── layout.tsx
    │   └── api/chat/route.ts   # Next.js proxy → FastAPI /chat
    └── components/
        ├── ChatMessage.tsx     # react-markdown + remark-gfm (table support)
        ├── TypingIndicator.tsx # Bouncing dots loading animation
        └── PortfolioChart.tsx  # recharts line chart, normalized to 100
```

### Tool-calling agentic loop

1. Frontend `POST /api/chat` → Next.js proxy → FastAPI `POST /chat`
2. `claude_client.py` loops: sends messages + tool definitions to Claude
3. `stop_reason == "tool_use"` → execute tool, append result, repeat
4. `stop_reason == "end_turn"` → return text; `"max_tokens"` → return partial text

### Tools

| Tool | Source | Description |
|------|--------|-------------|
| `get_stock_quote` | yfinance | Real-time price, market cap, 52w range |
| `get_financials` | yfinance | Annual income statement highlights |
| `get_risk_metrics` | yfinance | Volatility, beta vs SPY, Sharpe ratio |
| `compare_stocks` | yfinance | Multi-stock P/E, EPS, revenue growth, beta, YTD return |
| `get_portfolio_analysis` | yfinance | Weighted beta/vol, CFA risk contribution % |
| `get_cpi` | FRED | CPI readings + MoM change |
| `get_interest_rate` | FRED | Fed Funds, 10Y/2Y Treasury, unemployment |

### Portfolio Chart

`POST /portfolio/history` — returns daily normalized price series (base = 100) for each holding and the weighted portfolio. Used by `PortfolioChart.tsx`.

## Commands

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in API keys

uvicorn main:app --reload --port 8000

pytest tests/test_tools.py::test_stock_quote -v
pytest tests/ -v
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev        # localhost:3000
npm run build
npm run lint
```

## Environment Variables

```
# backend/.env
ANTHROPIC_API_KEY=
FRED_API_KEY=       # https://fred.stlouisfed.org/docs/api/api_key.html

# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key Implementation Notes

- **NaN safety:** yfinance can return `float('nan')`. All tool results go through `_SafeEncoder` in `claude_client.py` before `json.dumps` — never bypass this.
- **Adding a tool:** (1) implement in `tools/stock.py` or `tools/macro.py`, (2) register in `tools/__init__.py` `TOOL_MAP`, (3) add JSON Schema to `tool_definitions.py`.
- **System prompt language:** Written in English. Claude responds in the user's language (English → English, Chinese → Traditional Chinese). Keep responses to 3-4 bullet points per section.
- **FRED series IDs:** `CPIAUCSL` (CPI), `FEDFUNDS` (Fed Funds), `DGS10` (10Y Treasury), `DGS2` (2Y Treasury), `UNRATE` (unemployment).
- **yfinance:** `.info` for metadata/quotes, `.financials` for income statement (columns = fiscal years, most recent is `iloc[:,0]`), `.history(period=)` for OHLCV.
- **IME input:** Enter key send is gated on `!e.nativeEvent.isComposing` to prevent firing during Chinese IME composition.

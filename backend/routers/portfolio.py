import asyncio
import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class Holding(BaseModel):
    symbol: str
    weight: float  # decimal (0.30) or percent (30) — normalized below


class PortfolioHistoryRequest(BaseModel):
    holdings: list[Holding]
    period: str = "1y"  # 1mo, 3mo, 6mo, 1y, 2y


@router.post("/history")
async def portfolio_history(request: PortfolioHistoryRequest):
    symbols = [h.symbol.upper() for h in request.holdings]
    raw_weights = np.array([h.weight for h in request.holdings])

    if raw_weights.sum() > 1.5:
        raw_weights = raw_weights / 100.0
    weights = raw_weights / raw_weights.sum()

    def _fetch():
        raw = yf.download(
            symbols, period=request.period, auto_adjust=True, progress=False
        )
        prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(symbols[0])
        return prices[symbols].dropna()

    prices = await asyncio.to_thread(_fetch)

    if prices.empty or len(prices) < 5:
        raise HTTPException(status_code=422, detail="Insufficient price history")

    # Normalize each stock to 100 on first day
    normalized = prices / prices.iloc[0] * 100

    # Weighted portfolio value
    normalized["Portfolio"] = (normalized * weights).sum(axis=1)

    # Build response: [{date, Portfolio, AAPL, NVDA, ...}, ...]
    normalized.index = pd.to_datetime(normalized.index)
    records = []
    for date, row in normalized.iterrows():
        entry = {"date": date.strftime("%Y-%m-%d")}
        for col in normalized.columns:
            entry[col] = round(float(row[col]), 2)
        records.append(entry)

    return {
        "period": request.period,
        "symbols": symbols,
        "weights": {sym: round(float(w), 4) for sym, w in zip(symbols, weights)},
        "data": records,
    }

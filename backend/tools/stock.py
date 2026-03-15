import yfinance as yf
import pandas as pd
import numpy as np


def get_stock_quote(symbol: str) -> dict:
    """Get real-time stock quote for a given ticker symbol."""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "symbol": symbol.upper(),
        "name": info.get("longName"),
        "price": info.get("currentPrice") or info.get("regularMarketPrice"),
        "previous_close": info.get("previousClose"),
        "change_percent": info.get("regularMarketChangePercent"),
        "market_cap": info.get("marketCap"),
        "volume": info.get("volume"),
        "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
        "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        "currency": info.get("currency"),
    }


def get_financials(symbol: str) -> dict:
    """Get latest annual income statement highlights for a ticker."""
    ticker = yf.Ticker(symbol)
    info = ticker.info

    financials = ticker.financials  # columns = fiscal years
    if financials is None or financials.empty:
        return {"error": f"No financial data available for {symbol}"}

    latest = financials.iloc[:, 0]  # most recent year
    return {
        "symbol": symbol.upper(),
        "period": str(financials.columns[0].date()),
        "total_revenue": _safe(latest, "Total Revenue"),
        "gross_profit": _safe(latest, "Gross Profit"),
        "operating_income": _safe(latest, "Operating Income"),
        "net_income": _safe(latest, "Net Income"),
        "ebitda": info.get("ebitda"),
        "pe_ratio": info.get("trailingPE"),
        "eps": info.get("trailingEps"),
    }


def get_risk_metrics(symbol: str, period: str = "1y") -> dict:
    """Calculate simple risk metrics: volatility, beta, Sharpe ratio."""
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)

    if hist.empty:
        return {"error": f"No price history for {symbol}"}

    returns = hist["Close"].pct_change().dropna()
    annual_vol = float(returns.std() * (252 ** 0.5))

    # Use SPY as market benchmark for beta
    spy = yf.Ticker("SPY").history(period=period)["Close"].pct_change().dropna()
    aligned = pd.concat([returns, spy], axis=1).dropna()
    aligned.columns = ["stock", "market"]
    cov = aligned.cov().iloc[0, 1]
    market_var = aligned["market"].var()
    beta = float(cov / market_var) if market_var != 0 else None

    risk_free_rate = 0.05 / 252  # approximate daily risk-free rate
    excess_returns = returns - risk_free_rate
    sharpe = float(excess_returns.mean() / returns.std() * (252 ** 0.5))

    return {
        "symbol": symbol.upper(),
        "period": period,
        "annualized_volatility": round(annual_vol, 4),
        "beta_vs_spy": round(beta, 4) if beta is not None else None,
        "sharpe_ratio": round(sharpe, 4),
    }


def compare_stocks(symbols: list) -> dict:
    """
    Fetch valuation & performance metrics for multiple stocks simultaneously.
    Returns per-stock: P/E, Forward P/E, PEG, EPS, Revenue Growth (YoY),
    Beta, YTD return, Profit Margin, and Debt/Equity.
    """
    from datetime import date

    ytd_start = date(date.today().year, 1, 1).strftime("%Y-%m-%d")
    symbols = [s.upper() for s in symbols]

    # Batch-download YTD prices in one call
    raw = yf.download(symbols, start=ytd_start, auto_adjust=True, progress=False)
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(symbols[0])

    results = []
    for sym in symbols:
        ticker = yf.Ticker(sym)
        info = ticker.info

        # YTD return
        ytd_return = None
        if sym in prices.columns:
            col = prices[sym].dropna()
            if len(col) >= 2:
                ytd_return = round((float(col.iloc[-1]) / float(col.iloc[0]) - 1) * 100, 2)

        # Revenue growth YoY from financials
        rev_growth = None
        try:
            fin = ticker.financials
            if fin is not None and not fin.empty and fin.shape[1] >= 2:
                rev = fin.loc["Total Revenue"] if "Total Revenue" in fin.index else None
                if rev is not None and pd.notna(rev.iloc[0]) and pd.notna(rev.iloc[1]) and rev.iloc[1] != 0:
                    rev_growth = round((float(rev.iloc[0]) / float(rev.iloc[1]) - 1) * 100, 2)
        except Exception:
            pass

        results.append({
            "symbol": sym,
            "name": info.get("longName"),
            "sector": info.get("sector"),
            # Valuation
            "trailing_pe": _round(info.get("trailingPE")),
            "forward_pe": _round(info.get("forwardPE")),
            "peg_ratio": _round(info.get("pegRatio")),
            "price_to_book": _round(info.get("priceToBook")),
            # Earnings & Growth
            "eps_ttm": _round(info.get("trailingEps")),
            "eps_forward": _round(info.get("forwardEps")),
            "revenue_growth_yoy_pct": rev_growth,
            "earnings_growth_yoy_pct": _round_pct(info.get("earningsGrowth")),
            # Risk
            "beta": _round(info.get("beta")),
            # Profitability
            "profit_margin_pct": _round_pct(info.get("profitMargins")),
            "roe_pct": _round_pct(info.get("returnOnEquity")),
            "debt_to_equity": _round(info.get("debtToEquity")),
            # Performance
            "ytd_return_pct": ytd_return,
            "52w_return_pct": _round_pct(info.get("52WeekChange")),
        })

    return {"symbols": symbols, "stocks": results}


def _round(val, n: int = 2):
    try:
        return round(float(val), n) if val is not None and not (isinstance(val, float) and np.isnan(val)) else None
    except Exception:
        return None


def _round_pct(val, n: int = 2):
    """Convert decimal ratio to percentage and round."""
    try:
        return round(float(val) * 100, n) if val is not None and not (isinstance(val, float) and np.isnan(val)) else None
    except Exception:
        return None


def get_portfolio_analysis(holdings: list, period: str = "1y") -> dict:
    """
    CFA-framework portfolio risk analysis.

    holdings: [{"symbol": "AAPL", "weight": 0.30}, ...]
    Weights are auto-normalized so they don't need to sum to exactly 1.

    Outputs:
    - Portfolio annualized volatility: sqrt(w^T Σ w)
    - Portfolio weighted beta vs SPY
    - Per-holding risk contribution % (CFA marginal risk contribution):
        RC_i = w_i * (Σw)_i / σ_p,  %RC_i = RC_i / σ_p
    """
    symbols = [h["symbol"].upper() for h in holdings]
    raw_weights = np.array([float(h["weight"]) for h in holdings])

    # Accept weights as % (e.g. 30) or decimal (0.30) — normalize either way
    if raw_weights.sum() > 1.5:
        raw_weights = raw_weights / 100.0
    weights = raw_weights / raw_weights.sum()

    # Download all price history in one call
    raw = yf.download(symbols, period=period, auto_adjust=True, progress=False)
    prices = raw["Close"] if isinstance(raw.columns, pd.MultiIndex) else raw
    if isinstance(prices, pd.Series):
        prices = prices.to_frame(symbols[0])
    prices = prices[symbols]  # ensure column order matches weights

    returns = prices.pct_change().dropna()
    if returns.empty or len(returns) < 20:
        return {"error": "Insufficient price history for analysis"}

    # SPY for beta calculation
    spy_returns = (
        yf.Ticker("SPY").history(period=period, auto_adjust=True)["Close"]
        .pct_change()
        .dropna()
        .rename("SPY")
    )
    combined = pd.concat([returns, spy_returns], axis=1).dropna()
    stock_returns = combined[symbols]
    spy_ret = combined["SPY"]

    # Annualized covariance matrix
    cov_matrix = stock_returns.cov().values * 252
    market_var = float(spy_ret.var() * 252)

    # Per-stock beta and individual volatility
    betas = []
    indiv_vols = []
    for sym in symbols:
        cov_with_market = float(stock_returns[sym].cov(spy_ret) * 252)
        betas.append(cov_with_market / market_var if market_var else 0.0)
        indiv_vols.append(float(stock_returns[sym].std() * np.sqrt(252)))

    # Portfolio-level metrics
    portfolio_variance = float(weights @ cov_matrix @ weights)
    portfolio_vol = float(np.sqrt(portfolio_variance))
    weighted_beta = float(np.dot(weights, betas))

    # CFA risk contribution
    # MCR_i = (Σw)_i / σ_p  (marginal contribution to risk)
    # RC_i  = w_i * MCR_i   (absolute risk contribution, sums to σ_p)
    # %RC_i = RC_i / σ_p    (percentage risk contribution, sums to 100%)
    sigma_w = cov_matrix @ weights
    rc = weights * sigma_w / portfolio_vol
    pct_rc = rc / portfolio_vol  # sums to 1.0

    return {
        "period": period,
        "portfolio_annualized_volatility": round(portfolio_vol, 4),
        "portfolio_weighted_beta": round(weighted_beta, 4),
        "diversification_ratio": round(
            float(np.dot(weights, indiv_vols)) / portfolio_vol, 4
        ),
        "holdings": [
            {
                "symbol": sym,
                "weight_pct": round(float(weights[i]) * 100, 2),
                "beta": round(betas[i], 4),
                "annualized_volatility": round(indiv_vols[i], 4),
                "risk_contribution_pct": round(float(pct_rc[i]) * 100, 2),
            }
            for i, sym in enumerate(symbols)
        ],
    }


def _safe(series: pd.Series, key: str):
    try:
        val = series.get(key)
        return int(val) if pd.notna(val) else None
    except Exception:
        return None

TOOLS = [
    {
        "name": "get_stock_quote",
        "description": "Get real-time stock quote including price, change, market cap, and 52-week range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock ticker symbol, e.g. AAPL, TSLA, 2330.TW"},
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_financials",
        "description": "Get the latest annual income statement highlights for a stock: revenue, profit, EPS, P/E ratio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock ticker symbol"},
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "get_risk_metrics",
        "description": "Calculate risk metrics for a stock: annualized volatility, beta vs SPY, and Sharpe ratio.",
        "input_schema": {
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Stock ticker symbol"},
                "period": {
                    "type": "string",
                    "description": "Lookback period: '1mo', '3mo', '6mo', '1y', '2y'. Defaults to '1y'.",
                    "enum": ["1mo", "3mo", "6mo", "1y", "2y"],
                },
            },
            "required": ["symbol"],
        },
    },
    {
        "name": "compare_stocks",
        "description": (
            "Fetch valuation and performance metrics for multiple stocks at once and compare them. "
            "Returns P/E (trailing & forward), PEG ratio, P/B, EPS, revenue & earnings growth YoY, "
            "beta, profit margin, ROE, debt/equity, YTD return, and 52-week return. "
            "After receiving the data, apply the CFA relative valuation framework: "
            "(1) Relative value: compare trailing/forward P/E to sector peers and historical averages — "
            "lower P/E vs peers may signal undervaluation, but check earnings quality. "
            "(2) Growth-adjusted value: use PEG ratio (P/E ÷ growth rate) — PEG < 1 often indicates "
            "attractive growth-adjusted pricing. "
            "(3) Profitability & moat: ROE and profit margin indicate competitive advantage. "
            "(4) Risk-adjusted lens: higher beta = higher systematic risk; pair with return premium. "
            "(5) Balance sheet health: debt/equity flags leverage risk. "
            "Summarize with a CFA-style conclusion on which stock offers the best risk-adjusted value."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "symbols": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of stock ticker symbols to compare, e.g. ['AAPL', 'MSFT', 'GOOGL']",
                },
            },
            "required": ["symbols"],
        },
    },
    {
        "name": "get_portfolio_analysis",
        "description": (
            "CFA-framework portfolio risk analysis for multiple stocks. "
            "Returns portfolio annualized volatility (sqrt(w^T Σ w)), weighted beta vs SPY, "
            "diversification ratio, and per-holding risk contribution % based on marginal risk contribution."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "holdings": {
                    "type": "array",
                    "description": "List of holdings with symbol and weight.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "symbol": {"type": "string", "description": "Stock ticker, e.g. AAPL"},
                            "weight": {
                                "type": "number",
                                "description": "Portfolio weight as decimal (0.30) or percentage (30). Will be normalized.",
                            },
                        },
                        "required": ["symbol", "weight"],
                    },
                },
                "period": {
                    "type": "string",
                    "description": "Lookback period for returns: '1mo', '3mo', '6mo', '1y', '2y'. Defaults to '1y'.",
                    "enum": ["1mo", "3mo", "6mo", "1y", "2y"],
                },
            },
            "required": ["holdings"],
        },
    },
    {
        "name": "get_cpi",
        "description": "Get recent CPI (Consumer Price Index) data from FRED, including month-over-month change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "months": {
                    "type": "integer",
                    "description": "Number of recent months to return. Defaults to 6.",
                },
            },
        },
    },
    {
        "name": "get_interest_rate",
        "description": "Get interest rate data from FRED. Supports fed funds rate, 10Y/2Y treasury yields, and unemployment rate.",
        "input_schema": {
            "type": "object",
            "properties": {
                "rate_type": {
                    "type": "string",
                    "description": "Type of rate to fetch.",
                    "enum": ["fed_funds", "treasury_10y", "treasury_2y", "unemployment"],
                },
            },
        },
    },
]

from .stock import get_stock_quote, get_financials, get_risk_metrics, get_portfolio_analysis, compare_stocks
from .macro import get_cpi, get_interest_rate

TOOL_MAP = {
    "get_stock_quote": get_stock_quote,
    "get_financials": get_financials,
    "get_risk_metrics": get_risk_metrics,
    "get_portfolio_analysis": get_portfolio_analysis,
    "compare_stocks": compare_stocks,
    "get_cpi": get_cpi,
    "get_interest_rate": get_interest_rate,
}

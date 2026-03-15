"""Basic smoke tests for tool functions."""
import pytest
from tools.stock import get_stock_quote, get_risk_metrics


def test_stock_quote():
    result = get_stock_quote("AAPL")
    assert result["symbol"] == "AAPL"
    assert result["price"] is not None


def test_stock_quote_invalid():
    result = get_stock_quote("INVALIDXYZ999")
    # yfinance returns empty info; price will be None
    assert "symbol" in result


def test_risk_metrics():
    result = get_risk_metrics("AAPL", period="3mo")
    assert "annualized_volatility" in result
    assert "beta_vs_spy" in result
    assert "sharpe_ratio" in result

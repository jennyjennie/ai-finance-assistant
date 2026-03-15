import os
import requests
from datetime import datetime, timedelta

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

SERIES = {
    "cpi": "CPIAUCSL",
    "fed_funds": "FEDFUNDS",
    "treasury_10y": "DGS10",
    "treasury_2y": "DGS2",
    "unemployment": "UNRATE",
}


def _fetch_fred(series_id: str, limit: int = 12) -> list[dict]:
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError("FRED_API_KEY not set")

    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "desc",
        "limit": limit,
    }
    resp = requests.get(FRED_BASE_URL, params=params, timeout=10)
    resp.raise_for_status()
    observations = resp.json().get("observations", [])
    return [
        {"date": o["date"], "value": o["value"]}
        for o in observations
        if o["value"] != "."
    ]


def get_cpi(months: int = 6) -> dict:
    """Get recent CPI (Consumer Price Index) readings from FRED."""
    data = _fetch_fred(SERIES["cpi"], limit=months + 1)
    if len(data) < 2:
        return {"error": "Insufficient CPI data"}

    latest = data[0]
    prev = data[1]
    mom_change = (float(latest["value"]) - float(prev["value"])) / float(prev["value"]) * 100

    return {
        "series": "CPI (CPIAUCSL)",
        "latest_date": latest["date"],
        "latest_value": float(latest["value"]),
        "mom_change_pct": round(mom_change, 3),
        "recent_readings": data[:months],
    }


def get_interest_rate(rate_type: str = "fed_funds") -> dict:
    """
    Get interest rate data from FRED.
    rate_type options: 'fed_funds', 'treasury_10y', 'treasury_2y', 'unemployment'
    """
    series_id = SERIES.get(rate_type)
    if not series_id:
        return {"error": f"Unknown rate_type '{rate_type}'. Options: {list(SERIES.keys())}"}

    data = _fetch_fred(series_id, limit=6)
    if not data:
        return {"error": f"No data for {rate_type}"}

    latest = data[0]
    return {
        "series": f"{rate_type} ({series_id})",
        "latest_date": latest["date"],
        "latest_value": float(latest["value"]),
        "recent_readings": data,
    }

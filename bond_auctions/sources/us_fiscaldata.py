import datetime as _dt
import math
from typing import List, Optional, Dict, Any
import pandas as pd
import requests

_BASE = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
_ENDPOINT = "/v1/accounting/od/auctions_query"

# Map a row to a friendly tenor label (6m/1y/5y/10y...) based on security type & term.
def _normalize_tenor(row: pd.Series) -> Optional[str]:
    stype = (row.get("security_type") or "").lower()
    term = row.get("security_term")
    # security_term is in months for Bills, and years for Notes/Bonds/FRNs/TIPS in this dataset.
    try:
        term = float(term) if term is not None and str(term).strip() != "" else None
    except Exception:
        term = None
    if term is None:
        return None
    if "bill" in stype:
        months = term  # already months
        if math.isclose(months, 1, rel_tol=1e-3): return "1m"
        if math.isclose(months, 2, rel_tol=1e-3): return "2m"
        if math.isclose(months, 3, rel_tol=1e-3): return "3m"
        if math.isclose(months, 4, rel_tol=1e-3): return "4m"
        if math.isclose(months, 6, rel_tol=1e-3): return "6m"
        if math.isclose(months, 12, rel_tol=1e-3): return "1y"
        return f"{int(months)}m"
    else:
        years = term  # for notes/bonds
        if math.isclose(years, 1, rel_tol=1e-3): return "1y"
        if math.isclose(years, 2, rel_tol=1e-3): return "2y"
        if math.isclose(years, 3, rel_tol=1e-3): return "3y"
        if math.isclose(years, 5, rel_tol=1e-3): return "5y"
        if math.isclose(years, 7, rel_tol=1e-3): return "7y"
        if math.isclose(years, 10, rel_tol=1e-3): return "10y"
        if math.isclose(years, 20, rel_tol=1e-3): return "20y"
        if math.isclose(years, 30, rel_tol=1e-3): return "30y"
        return f"{int(years)}y"

def fetch_us_auctions(start: str, end: str, tenors: Optional[List[str]] = None) -> pd.DataFrame:
    """Fetch completed US Treasury auctions between [start, end] (YYYY-MM-DD), filtered by tenor labels.
    Returns a normalized DataFrame.
    """
    # Fields we'll request; many more are available.
    fields = [
        "auction_date","issue_date","security_type","security_term","cusip",
        "offering_amount","tendered_total","accepted_total","bid_to_cover_ratio",
        "high_yield","low_yield","median_yield","high_discount_rate","high_investment_rate",
        "price_per_100","auction_format","security_desc","announcement_date"
    ]
    params = {
        "fields": ",".join(fields),
        "filter": f"auction_date:gte:{start},auction_date:lte:{end}",
        "sort": "-auction_date",
        "page[size]": 10000
    }
    url = _BASE + _ENDPOINT
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    data = r.json().get("data", [])
    df = pd.DataFrame(data)
    if df.empty:
        return df

    # Numeric conversions
    num_cols = [
        "security_term","offering_amount","tendered_total","accepted_total",
        "bid_to_cover_ratio","high_yield","low_yield","median_yield",
        "high_discount_rate","high_investment_rate","price_per_100"
    ]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    # Dates
    date_cols = ["auction_date","issue_date","announcement_date"]
    for c in date_cols:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce").dt.date

    # Tenor label
    df["tenor"] = df.apply(_normalize_tenor, axis=1)

    # Filter by tenor if requested
    if tenors:
        want = set([t.strip().lower() for t in tenors])
        df = df[df["tenor"].str.lower().isin(want)]

    # Rename to a clean schema
    rename_map = {
        "auction_date": "auction_date",
        "issue_date": "issue_date",
        "announcement_date": "announcement_date",
        "security_type": "security_type",
        "security_term": "term_raw",
        "tenor": "tenor",
        "cusip": "cusip",
        "security_desc": "security_desc",
        "offering_amount": "amount_offered",
        "tendered_total": "amount_tendered",
        "accepted_total": "amount_accepted",
        "bid_to_cover_ratio": "bid_to_cover",
        "high_yield": "high_yield",
        "low_yield": "low_yield",
        "median_yield": "median_yield",
        "high_discount_rate": "high_discount_rate",
        "high_investment_rate": "high_investment_rate",
        "price_per_100": "price_per_100",
        "auction_format": "auction_format"
    }
    out_cols = [v for v in rename_map.values()]
    df = df.rename(columns=rename_map)
    # Ensure all columns present
    for c in out_cols:
        if c not in df.columns:
            df[c] = pd.NA
    # Order columns
    df = df[out_cols]
    return df

import argparse
import sys
from typing import List, Optional
import pandas as pd

from bond_auctions.sources.us_fiscaldata import fetch_us_auctions

SUPPORTED = {"us"}

def parse_args():
    p = argparse.ArgumentParser(description="Fetch completed government bond auction data.")
    p.add_argument("--country", required=True, help="Country code: us")
    p.add_argument("--start", required=True, help="Start date YYYY-MM-DD")
    p.add_argument("--end", required=True, help="End date YYYY-MM-DD")
    p.add_argument("--tenors", default="", help="Comma-separated tenors to include, e.g. 6m,1y,5y,10y. Default: all")
    p.add_argument("--out", default="", help="Path to output CSV (default: auctions_<country>.csv)")
    return p.parse_args()

def fetch(country: str, start: str, end: str, tenors: Optional[List[str]]):
    country = country.lower()
    if country == "us":
        return fetch_us_auctions(start, end, tenors)
    raise SystemExit(f"Country '{country}' is not yet implemented. Supported: {', '.join(sorted(SUPPORTED))}")

def main():
    a = parse_args()
    tenors = [t.strip().lower() for t in a.tenors.split(",") if t.strip()] or None
    df = fetch(a.country, a.start, a.end, tenors)
    if df.empty:
        print("No rows returned for the selected filters.")
        sys.exit(0)
    outpath = a.out or f"auctions_{a.country}.csv"
    df.to_csv(outpath, index=False)
    # Show a compact preview
    preview_cols = [c for c in ["auction_date","tenor","security_type","amount_offered","amount_accepted","bid_to_cover","high_yield"] if c in df.columns]
    print(df[preview_cols].head(20).to_string(index=False))
    print(f"\nSaved {len(df):,} rows -> {outpath}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

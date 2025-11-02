# Bond Auction Fetcher

Fetches **completed government bond auction** data for a selected country and date range and filters by tenor (6m, 1y, 5y, 10y).  
Currently implemented: **United States (US)** via the U.S. Treasury **Fiscal Data API** (`auctions_query`).

> Other countries (UK DMO, Germany Finanzagentur, Italy MEF, European Commission EU-Bonds) are scaffolded as adapters and can be added easily. See the notes in `bond_auctions/sources/` and the links below.

## Quick start

```bash
python -m venv .venv
. .venv/Scripts/activate    # Windows
# or: source .venv/bin/activate
pip install -r requirements.txt
python main.py --country us --start 2024-01-01 --end 2025-11-02 --tenors 6m,1y,5y,10y --out auctions_us.csv
```

This saves `auctions_us.csv` with normalized columns, and prints a preview table.

## CLI

```
python main.py --country COUNTRY --start YYYY-MM-DD --end YYYY-MM-DD [--tenors 6m,1y,5y,10y] [--out FILE]
```

- `--country` currently supports: `us`
- `--tenors` comma-separated; supported aliases: `6m, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y`; defaults to all.
- `--out` optional path to CSV file; default: `auctions_<country>.csv` in the current directory.

## Data sources (implemented / ready to add)
- **United States** — U.S. Treasury Fiscal Data API (`auctions_query`) – documented here:  
  https://fiscaldata.treasury.gov/api-documentation/  and dataset summary: https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/  

- **United Kingdom (planned adapter)** — UK DMO “Outright Gilt Auctions” (Excel/CSV): https://www.dmo.gov.uk/data/gilt-market/results-of-gilt-operations/ and data report `D2.1A`.  
- **Germany (planned adapter)** — Deutsche Finanzagentur “Auktionsergebnisse” (PDF/CSV via Downloadcenter): https://www.deutsche-finanzagentur.de/downloadcenter  
- **Italy (planned adapter)** — MEF Treasury “Auction and placement results”: https://www.dt.mef.gov.it/en/debito_pubblico/emissioni_titoli_di_stato_interni/risultati_aste/  
- **European Commission (planned adapter)** — EU-Bonds auction announcements & results: https://commission.europa.eu/.../auction-announcements-and-results_en

## Notes

- The **US adapter** queries the official API and normalizes fields like: `auction_date`, `security_type`, `security_term`, `offering_amount`, `accepted_amount`, `bid_to_cover_ratio`, `high_yield`, etc.  
- Tenor mapping is done from the numeric `security_term` and `security_type` (e.g., Bills in months, Notes/Bonds in years). See `bond_auctions/sources/us_fiscaldata.py` for details.
- For countries publishing **Excel/PDF**, consider adding an adapter using `pandas.read_excel` or a PDF table extractor (e.g., `pdfplumber`).

## License
MIT

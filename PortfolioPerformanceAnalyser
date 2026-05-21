
# Grug's Portfolio Analyser

## Summary
---
A command-line Python tool that reads a CSV file of share trades and produces a plain-English breakdown of an Australian share portfolio. It fetches live prices from Yahoo Finance, calculates gains and losses, ranks holdings by performance, flags concentration risk, and pulls ETF profile data — all formatted for easy reading without financial jargon.

**Run it:**
```bash
python portfolio.py trades.csv
# or just:
python portfolio.py   # it will ask for the path
```

**Required CSV columns:** `market_code`, `transaction_type` (BUY/SELL), `instrument_code`, `trade_date` (DD/MM/YYYY), `quantity`, `price`, `amount`

---

## Parts
---
| Module / Function | Purpose |
|---|---|
| `load_data()` | Reads and cleans the trades CSV into a normalised DataFrame |
| `get_holdings()` | Calculates current share quantities (buys minus sells) |
| `get_prices()` | Fetches today's closing price for each holding via yfinance (.AX suffix for ASX) |
| `portfolio_summary()` | Aggregates current value, capital invested, and total return |
| `print_summary()` | Prints the top-level portfolio overview table |
| `get_holding_performance()` | Per-ticker return, grade, annualised return, and dollar gain |
| `print_performance_ranking()` | Ranked display of each holding from best to worst |
| `print_concentration_warning()` | Bar chart of portfolio weights; warns if any holding exceeds 30% |
| `get_etf_data()` | Pulls ETF metadata (expense ratio, top holdings, sector weights) via yfinance |
| `full_etf_report()` | Prints a plain-English ETF profile card for each ETF in the portfolio |
| `print_activity_summary()` | High-level trade history stats (counts, date range, total spend) |

**Helper formatters:** `dollars()`, `pct()`, `grade()`, `plain_duration()`, `yearly_return_plain()`, `fee_verdict()`, `risk_plain()`

---

## Design and Logic
---

### Holdings Calculation
Trades are sorted by date and applied sequentially. BUY adds quantity; SELL subtracts it. Any ticker with a remaining quantity below `1e-7` (i.e. fully sold) is excluded from the active holdings dict.

### Performance Measurement
Each holding's return is measured from the **first buy date** to today using Yahoo Finance historical data. This gives a price-based total return rather than a cost-basis return. Dollar gain (`your_gain_$`) is computed using the **average cost** across all buy trades, giving a more personalised profit figure.

### Annualised Return
Uses CAGR formula: `((1 + total_pct/100) ^ (1/years) - 1) * 100`. Presented in plain language ("~12.3% per year on average") rather than financial terminology.

### Grading System
Simple letter grade based on total return from first purchase:

| Grade | Return |
|---|---|
| A+ | ≥ 50% |
| A  | ≥ 25% |
| B  | ≥ 10% |
| C  | ≥ 0%  |
| D  | ≥ -10% |
| F  | < -10% |

### Concentration Warning
Portfolio weights are computed as a proportion of total current value. Any holding exceeding **30%** triggers a plain-language warning encouraging the user to consider the risk.

### ETF Detection
All current holdings are passed through `full_etf_report()`. If yfinance returns no fund-specific data (no expense ratio, no assets, no top holdings), the report is silently skipped — the ticker is treated as a regular share.

---

## Code
---

```python
# Key dependencies
import pandas as pd
import yfinance as yf
from datetime import date

# ASX ticker format used throughout
yf.Ticker(f"{ticker}.AX").history(period="1d")

# Holdings derived from net BUY minus SELL quantity
counts[t] = counts.get(t, 0) + delta  # delta positive for BUY, negative for SELL

# CAGR annualisation
cagr = ((1 + total_pct / 100) ** (1 / years) - 1) * 100

# Concentration weight
weights = {t: v / total * 100 for t, v in values.items()}
```

Full source: `portfolio.py`

---

## Challenges Faced + Solutions
---

**1. ASX Ticker Format**
Yahoo Finance requires `.AX` appended to ASX codes (e.g. `VAS` → `VAS.AX`). The CSV stores bare instrument codes, so the suffix is applied at fetch time.

**2. ETF vs Share Detection**
There's no explicit ETF flag in the CSV. The solution is duck-typing: attempt to fetch ETF-specific fields; if all three (expense ratio, total assets, top holdings) come back empty, treat it as a regular share and skip the ETF report.

**3. Partially Sold Holdings**
A ticker may have been partially sold. The `get_holdings()` function handles this by running a running net-quantity tally and filtering out anything below `1e-7` at the end, which covers floating-point dust from partial sales.

**4. Missing or Bad Data in CSV**
Column names may have inconsistent spacing or casing. `load_data()` strips, lowercases, and normalises all column names, and coerces numeric/date fields with `errors="coerce"` so bad rows silently become `NaN` rather than crashing the program.

**5. yfinance History Gaps**
For very new listings or thinly traded ETFs, `hist.empty` may be `True`. Every `yf.history()` call is guarded with an `if not hist.empty` check before accessing `.iloc`.

---

## Design Improvements
---

- **Web dashboard** — Replace the terminal output with a browser-based UI (e.g. using Streamlit or Dash) with interactive charts for value over time, allocation pie charts, and performance tables.

- **Realised vs unrealised returns** — Currently only unrealised (held) positions are tracked. Adding sold-position P&L would give a complete picture of total portfolio performance including exits.

- **Cost-basis accuracy** — The current average cost uses all buy trades equally. A FIFO or LIFO method would give more tax-accurate cost basis calculations, particularly for partial sells.

- **Dividend tracking** — yfinance exposes dividend history. Incorporating dividend income into total return would give a more accurate picture, especially for income-focused ETFs like `VHY` or `A200`.

- **Multi-currency support** — Currently assumes all holdings are AUD (ASX). Supporting US or international shares (without `.AX`) would broaden usefulness.

- **Caching** — Each run hits the yfinance API for every holding. Adding a simple file-based cache with a TTL (e.g. 15 minutes) would dramatically speed up repeated runs on the same day.

- **Alerting** — Add a flag or email notification when a holding drops below a user-defined threshold (e.g. -10% from purchase price).

- **Config file** — Move hardcoded thresholds (30% concentration limit, grade cutoffs) into a `config.yaml` so users can tune them without touching the source code.

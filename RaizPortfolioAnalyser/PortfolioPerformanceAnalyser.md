# Portfolio Analyser

## Summary
---
A two-file Python application for analysing an Australian share portfolio from a CSV of trades. `portfolio.py` is the core engine — it loads trade data, fetches live ASX prices via Yahoo Finance, and produces plain-English reports on holdings, performance, concentration risk, and ETF profiles. `portfolio_gui.py` wraps that engine in a dark-themed Tkinter desktop GUI with tabbed output, a file picker, and background threading so the UI stays responsive during price fetching.

**Run the GUI:**
```bash
python portfolio_gui.py
```

**Run the CLI directly:**
```bash
python portfolio.py trades.csv
# or:
python portfolio.py   # prompts for path
```

**Required CSV columns:** `market_code`, `transaction_type` (BUY/SELL), `instrument_code`, `trade_date` (DD/MM/YYYY), `quantity`, `price`, `amount`

**Dependencies:** `pandas`, `yfinance`, `tkinter` (stdlib)

---

## Parts
---

### `portfolio.py` — Core Engine

| Function | Purpose |
|---|---|
| `load_data()` | Reads and normalises the trades CSV into a clean DataFrame |
| `get_holdings()` | Calculates current quantity held per ticker (buys minus sells) |
| `get_prices()` | Fetches today's closing price for each holding via yfinance (`.AX` suffix) |
| `portfolio_summary()` | Aggregates current value, capital invested, and total return |
| `print_summary()` | Prints the top-level portfolio overview table |
| `get_holding_performance()` | Computes per-ticker return %, grade, annualised return, and dollar gain |
| `print_performance_ranking()` | Ranked display of each holding from best to worst |
| `print_concentration_warning()` | Bar chart of portfolio weights; warns if any holding exceeds 30% |
| `get_etf_data()` | Pulls ETF metadata (expense ratio, top holdings, sector weights) |
| `full_etf_report()` | Prints a plain-English ETF profile card |
| `print_activity_summary()` | High-level trade history stats (counts, date range, total spend) |
| `dollars()` | Formats a float as `$1,234.56` or `-$1,234.56` |
| `pct()` | Formats a float as `▲ 12.3%` or `▼ 4.1%` |
| `grade()` | Returns letter grade A+/A/B/C/D/F based on total return % |
| `plain_duration()` | Converts days to human-readable string (e.g. `2yr 3mo`) |
| `yearly_return_plain()` | Expresses CAGR as a plain sentence |
| `fee_verdict()` | Rates an ETF's expense ratio in plain English |
| `risk_plain()` | Translates beta + category into a plain risk summary sentence |

### `portfolio_gui.py` — Desktop GUI

| Component | Purpose |
|---|---|
| `PortfolioApp` (class) | Main `tk.Tk` window; owns all state and layout |
| `_build_ui()` | Constructs the top bar, file picker row, tab notebook, and status bar |
| `_browse()` | Opens a file dialog and sets the CSV path |
| `_run()` | Validates input and spawns the background analysis thread |
| `_analyse()` | Runs on a daemon thread; calls all `portfolio.py` print functions and captures output |
| `_etf_section()` | Captures ETF report output for all current holdings |
| `_capture()` | Redirects `stdout` to a `StringIO` buffer to capture print output from `portfolio.py` |
| `_display()` | Pushes captured section text into the appropriate tab widgets (on main thread via `after()`) |
| `_show_error()` | Displays a formatted error message across all tabs |
| `_write()` | Enables, clears, writes, and re-disables a `ScrolledText` widget |
| `_set_status()` | Updates the status bar label at the bottom of the window |

---

## Design and Logic
---

### Two-Layer Architecture
`portfolio.py` is deliberately kept as a pure CLI module — all output goes to `stdout` via `print()`. `portfolio_gui.py` imports it and uses `io.StringIO` + `sys.stdout` redirection inside `_capture()` to intercept that printed output and route it into the GUI tabs. This means the logic never needs to know whether it's running in a terminal or a GUI.

### Holdings Calculation
Trades are sorted by date and a running net-quantity tally is maintained per ticker. BUY adds quantity; SELL subtracts it. Tickers with remaining quantity below `1e-7` (fully sold, or floating-point dust) are excluded from active holdings.

### Performance Measurement
Each holding's return is measured from the **first buy date** to today using Yahoo Finance historical price data. Dollar gain uses the **average cost** across all buy trades for that ticker, giving a personalised profit figure rather than just a price movement.

### Annualised Return (CAGR)
```
cagr = ((1 + total_pct / 100) ^ (1 / years) - 1) * 100
```
Expressed as `~12.3% per year on average` rather than "CAGR" to keep output accessible.

### Grading System

| Grade | Total Return |
|---|---|
| A+ | ≥ 50% |
| A  | ≥ 25% |
| B  | ≥ 10% |
| C  | ≥ 0%  |
| D  | ≥ -10% |
| F  | < -10% |

### Concentration Warning
Portfolio weights are computed as a proportion of total current market value. Any single holding exceeding **30%** triggers a plain-language warning with context about the downside risk of that concentration.

### ETF Detection
All current holdings are passed through `full_etf_report()`. If yfinance returns no fund-specific data (no expense ratio, no total assets, no top holdings), the report is silently skipped — that ticker is treated as a regular share.

### Threading in the GUI
Price fetching from Yahoo Finance can take 10–20 seconds for a multi-stock portfolio. `_run()` spawns a daemon thread for `_analyse()` so the Tkinter main loop stays responsive. Results are pushed back to the main thread using `self.after(0, ...)` — the only safe way to update Tk widgets from a background thread.

---

## Code
---

### Stdout Capture Pattern (GUI → Engine bridge)
```python
def _capture(self, fn, *args) -> str:
    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    fn(*args)
    sys.stdout = old
    return buf.getvalue()
```

### ASX Ticker Format
```python
# Yahoo Finance requires .AX suffix for ASX-listed securities
yf.Ticker(f"{ticker}.AX").history(period="1d")
```

### Holdings Net Calculation
```python
delta = row["quantity"] if row["transaction_type"] == "BUY" else -row["quantity"]
counts[t] = counts.get(t, 0) + delta
```

### Thread-safe UI Update
```python
# Never update Tk widgets directly from a background thread
self.after(0, self._display, sections)
```

### CAGR Annualisation
```python
years = days / 365.25
cagr  = ((1 + total_pct / 100) ** (1 / years) - 1) * 100
```

### Concentration Weight
```python
weights = {t: v / total * 100 for t, v in values.items()}
heavy   = [(t, w) for t, w in weights.items() if w > 30]
```

---

## Challenges Faced + Solutions
---

**1. ASX Ticker Format**
Yahoo Finance requires `.AX` appended to ASX codes (e.g. `VAS` → `VAS.AX`). The CSV stores bare instrument codes, so the suffix is applied at every `yf.Ticker()` call rather than stored in the data.

**2. ETF vs Share Detection**
There is no explicit ETF flag in the CSV. The solution is duck-typing: attempt to fetch ETF-specific fields and check all three (expense ratio, total assets, top holdings) — if all come back empty, skip the ETF profile card silently.

**3. Partially Sold Holdings**
A ticker may have been partially sold across multiple transactions. The rolling net-quantity approach in `get_holdings()` handles this naturally, and the `1e-7` floor filters out floating-point rounding errors from repeated partial sells.

**4. Messy CSV Input**
Column names from brokerage exports often have inconsistent spacing and casing. `load_data()` strips, lowercases, and normalises all column names upfront, and uses `errors="coerce"` on numeric and date parsing so malformed rows become `NaN` rather than crashing the script.

**5. yfinance Empty History**
For recently listed securities or thinly traded ETFs, `hist.empty` may be `True`. Every `.history()` call is guarded with `if not hist.empty` before accessing `.iloc` to avoid `IndexError`.

**6. GUI Thread Safety**
Tkinter is not thread-safe. Running yfinance calls on the main thread would freeze the window. The analysis runs on a `daemon=True` background thread, and all widget updates are marshalled back to the main thread with `self.after(0, callback)`.

**7. Capturing Print Output for GUI Tabs**
`portfolio.py` was written as a CLI tool that prints directly to stdout. Rather than rewriting the entire engine to return strings, the GUI uses a `_capture()` helper that temporarily replaces `sys.stdout` with a `StringIO` buffer, calls the function, then restores stdout and returns the captured string.

---

## Design Improvements
---

- **Live charts** — Replace the text-based bar chart in the concentration section with a proper pie or donut chart using `matplotlib` or `plotly`, embedded in the Tkinter window via `FigureCanvasTkAgg`.

- **Portfolio value over time** — Reconstruct historical portfolio value by replaying trades against historical price data, then plot the equity curve. Currently only a snapshot of today's value is shown.

- **Realised P&L** — Sold positions are excluded from the current view. Adding a separate "Closed Positions" tab with realised gain/loss per trade would give a complete picture of total portfolio performance.

- **Dividend tracking** — yfinance exposes dividend history. Including dividend income in the total return calculation would give a more accurate result, especially for income ETFs like `VHY` or `A200`.

- **Cost-basis methods** — The current average cost approach is simple but not tax-accurate. Supporting FIFO or LIFO cost-basis methods would make the gain figures more useful for tax reporting.

- **Price caching** — Every run hits the Yahoo Finance API for all holdings. A file-based cache with a short TTL (e.g. 15 minutes) would speed up repeated runs and reduce API load.

- **Export to CSV / PDF** — Add a button in the GUI to export the current analysis results to a formatted PDF or CSV for record-keeping or sharing.

- **Config file** — Move hardcoded thresholds (30% concentration limit, grade cutoffs, warning colours) into a `config.yaml` so users can personalise behaviour without editing source code.

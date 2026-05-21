"""
portfolio.py  Portfolio Analyser
===========================================
Run:  python portfolio.py trades.csv
      python portfolio.py          (will ask for path)

CSV must have columns:
  market_code, transaction_type (BUY/SELL), instrument_code,
  trade_date (DD/MM/YYYY), quantity, price, amount
"""

import sys
import pandas as pd
import yfinance as yf
from datetime import date

#  LOAD & CLEAN

def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.lower().str.replace(r"\s+", "_", regex=True)

    for col in df.select_dtypes("object").columns:
        df[col] = df[col].str.strip().str.replace(r"\s+", " ", regex=True).replace("", pd.NA)

    df["market_code"]      = df["market_code"].str.upper()
    df["transaction_type"] = df["transaction_type"].str.upper()
    df["instrument_code"]  = df["instrument_code"].str.upper()
    df["trade_date"]       = pd.to_datetime(df["trade_date"], format="%d/%m/%Y", errors="coerce")

    for col in ["quantity", "price", "amount"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

#  HOLDINGS & PRICES

def get_holdings(df: pd.DataFrame) -> dict[str, float]:
    counts: dict[str, float] = {}
    for _, row in df.sort_values("trade_date").iterrows():
        t     = row["instrument_code"]
        delta = row["quantity"] if row["transaction_type"] == "BUY" else -row["quantity"]
        counts[t] = counts.get(t, 0) + delta
    return {t: q for t, q in counts.items() if q > 1e-7}


def get_prices(holdings: dict) -> dict[str, float | None]:
    prices: dict[str, float | None] = {}
    for ticker in holdings:
        hist = yf.Ticker(f"{ticker}.AX").history(period="1d")
        prices[ticker] = float(hist["Close"].iloc[-1]) if not hist.empty else None
    return prices

#  HELPERS

def dollars(val: float) -> str:
    """Format as $1,234.56 or -$1,234.56"""
    if val < 0:
        return f"-${abs(val):,.2f}"
    return f"${val:,.2f}"


def pct(val: float) -> str:
    arrow = "▲" if val >= 0 else "▼"
    return f"{arrow} {abs(val):.1f}%"


def grade(total_return_pct: float) -> str:
    """Simple letter grade so anyone can read it at a glance."""
    if total_return_pct >= 50:  return "A+  "
    if total_return_pct >= 25:  return "A   "
    if total_return_pct >= 10:  return "B   "
    if total_return_pct >= 0:   return "C   "
    if total_return_pct >= -10: return "D    "
    return                             "F   "


def plain_duration(days: int) -> str:
    if days < 30:   return f"{days} days"
    if days < 365:  return f"{days // 30} months"
    years  = days // 365
    months = (days % 365) // 30
    return f"{years}yr {months}mo" if months else f"{years} year{'s' if years > 1 else ''}"


def yearly_return_plain(total_pct: float, days: int) -> str:
    """Express annualised return as plain words instead of 'CAGR'."""
    if days < 30:
        return "held < 1 month"
    years = days / 365.25
    cagr  = ((1 + total_pct / 100) ** (1 / years) - 1) * 100
    return f"~{cagr:+.1f}% per year on average"


#  PORTFOLIO SUMMARY


def portfolio_summary(df: pd.DataFrame) -> dict:
    holdings = get_holdings(df)
    prices   = get_prices(holdings)

    current_value    = sum(holdings[t] * prices[t] for t in holdings if prices[t])
    invested_capital = df.apply(
        lambda r: r["amount"] if r["transaction_type"] == "BUY" else -r["amount"], axis=1
    ).sum()
    total_return     = current_value - invested_capital
    total_return_pct = (total_return / invested_capital * 100) if invested_capital else 0

    return {
        "holdings":          {t: float(q) for t, q in holdings.items()},
        "prices":            prices,
        "current_value":     float(current_value),
        "invested_capital":  float(invested_capital),
        "total_return":      float(total_return),
        "total_return_pct":  float(total_return_pct),
    }


def print_summary(df: pd.DataFrame) -> None:
    s = portfolio_summary(df)

    ret     = s["total_return"]
    ret_pct = s["total_return_pct"]
    mood    = "Looking good! 📈" if ret >= 0 else "Portfolio is down overall. 📉"

    print(f"\n{'═'*60}")
    print("  YOUR PORTFOLIO  —  Quick Overview")
    print(f"{'═'*60}")
    print(f"\n  {mood}")
    print(f"\n  What your shares are worth today : {dollars(s['current_value'])}")
    print(f"  What you put in                  : {dollars(s['invested_capital'])}")

    gain_label = "Profit" if ret >= 0 else "Loss"
    print(f"  {gain_label} so far                     : {dollars(ret)}  ({pct(ret_pct)})")

    print(f"\n  ── Your Holdings ──")
    print(f"  {'Ticker':<8}  {'Shares':>8}  {'Price':>8}  {'Value':>10}")
    print(f"  {'─'*42}")
    for t, q in s["holdings"].items():
        p   = s["prices"].get(t) or 0
        val = q * p
        print(f"  {t:<8}  {q:>8.2f}  {dollars(p):>8}  {dollars(val):>10}")

    print(f"\n  Tip: Scroll down for a detailed breakdown of each holding.\n")


 
#  PERFORMANCE RANKING  (most interesting part for a layperson)


def get_holding_performance(df: pd.DataFrame) -> pd.DataFrame:
    holdings = get_holdings(df)
    buys     = df[df["transaction_type"] == "BUY"].copy()
    rows     = []

    for ticker, qty_held in holdings.items():
        ticker_buys = buys[buys["instrument_code"] == ticker].sort_values("trade_date")
        if ticker_buys.empty:
            continue

        first_buy_date = ticker_buys["trade_date"].iloc[0]
        avg_cost       = (ticker_buys["amount"].sum() / ticker_buys["quantity"].sum())

        hist = yf.Ticker(f"{ticker}.AX").history(start=first_buy_date.strftime("%Y-%m-%d"))
        if hist.empty:
            continue

        price_then       = float(hist["Close"].iloc[0])
        price_now        = float(hist["Close"].iloc[-1])
        total_return_pct = ((price_now - price_then) / price_then) * 100
        days             = (hist.index[-1] - hist.index[0]).days
        dollar_gain      = (price_now - avg_cost) * qty_held   # gain vs what YOU paid

        rows.append({
            "ticker":          ticker,
            "qty_held":        round(qty_held, 4),
            "avg_cost":        round(avg_cost, 3),
            "price_now":       round(price_now, 3),
            "total_return_%":  round(total_return_pct, 2),
            "your_gain_$":     round(dollar_gain, 2),
            "grade":           grade(total_return_pct),
            "held_for":        plain_duration(days),
            "yearly_return":   yearly_return_plain(total_return_pct, days),
            "first_buy":       first_buy_date.date(),
            "holding_days":    days,
        })

    perf = pd.DataFrame(rows).sort_values("total_return_%", ascending=False).reset_index(drop=True)
    perf.index += 1
    return perf


def print_performance_ranking(df: pd.DataFrame) -> None:
    perf = get_holding_performance(df)
    if perf.empty:
        print("  No performance data available.\n")
        return

    print(f"\n{'═'*70}")
    print("  HOW EACH HOLDING IS PERFORMING")
    print(f"  Ranked from best to worst, since you first bought\n")

    for rank, row in perf.iterrows():
        sign   = "+" if row["total_return_%"] >= 0 else ""
        g      = row["grade"]
        gain_s = dollars(row["your_gain_$"])

        print(f"  #{rank}  {row['ticker']:<6}  Grade: {g}")
        print(f"      You paid: {dollars(row['avg_cost'])} per share")
        print(f"      Now worth: {dollars(row['price_now'])} per share")
        print(f"      Change: {sign}{row['total_return_%']:.1f}%  ({gain_s} total)  —  {row['yearly_return']}")
        print(f"      Held for: {row['held_for']}  (since {row['first_buy']})")
        print()

    best   = perf.iloc[0]
    worst  = perf.iloc[-1]
    print(f"{'─'*70}")
    print(f"  🏆 Best performer : {best['ticker']}  ({best['total_return_%']:+.1f}%)")
    print(f"  ⚠️  Watch closely  : {worst['ticker']}  ({worst['total_return_%']:+.1f}%)")
    print(f"{'═'*70}\n")


#  CONCENTRATION WARNING  –  are you too exposed to one stock?


def print_concentration_warning(df: pd.DataFrame) -> None:
    holdings = get_holdings(df)
    prices   = get_prices(holdings)

    values = {t: holdings[t] * prices[t] for t in holdings if prices[t]}
    total  = sum(values.values())
    if total == 0:
        return

    weights = {t: v / total * 100 for t, v in values.items()}
    heavy   = [(t, w) for t, w in weights.items() if w > 30]

    print(f"\n{'═'*60}")
    print("  PORTFOLIO SPREAD  —  How spread out are your eggs?")
    print(f"{'═'*60}\n")

    for t, w in sorted(weights.items(), key=lambda x: -x[1]):
        bar = "█" * int(w / 2)
        print(f"  {t:<8} {w:>5.1f}%  {bar}")

    if heavy:
        print(f"\n  ⚠️  Heads up:")
        for t, w in heavy:
            print(f"     {t} makes up {w:.0f}% of your portfolio.")
            print(f"     If {t} drops sharply, it will hurt your overall results.")
            print(f"     Consider whether that concentration feels comfortable.")
    else:
        print(f"\n  ✅ Your portfolio is reasonably spread across holdings.\n")



#  ETF ANALYSIS  –  simplified & jargon-free

def get_etf_data(ticker: str) -> dict:
    etf  = yf.Ticker(ticker)
    info = etf.info or {}
    try:
        top_holdings   = etf.funds_data.top_holdings
        sector_weights = etf.funds_data.sector_weightings
    except Exception:
        top_holdings   = pd.DataFrame()
        sector_weights = {}
    return {
        "ticker":         ticker,
        "name":           info.get("longName", ticker),
        "category":       info.get("category", "Unknown"),
        "expense_ratio":  info.get("annualReportExpenseRatio") or info.get("expenseRatio"),
        "total_assets":   info.get("totalAssets"),
        "dividend_yield": info.get("yield"),
        "beta":           info.get("beta3Year") or info.get("beta"),
        "fund_family":    info.get("fundFamily"),
        "top_holdings":   top_holdings,
        "sector_weights": sector_weights,
    }


def fee_verdict(expense_ratio: float | None) -> str:
    if expense_ratio is None:
        return "Fee info not available"
    pct_val = expense_ratio * 100
    if pct_val < 0.10:
        return f"{pct_val:.2f}%/yr  Very cheap — excellent"
    if pct_val < 0.30:
        return f"{pct_val:.2f}%/yr  Reasonable"
    if pct_val < 0.60:
        return f"{pct_val:.2f}%/yr  On the pricier side"
    return     f"{pct_val:.2f}%/yr  Expensive — check if worth it"


def risk_plain(beta: float | None, category: str) -> str:
    """Replace 'Aggressive/Conservative' with plain sentences."""
    cat = (category or "").lower()
    b   = beta or 1.0
    if b >= 1.2 or any(k in cat for k in ["technology", "growth", "small", "emerging", "leveraged"]):
        return (f"Higher risk (tends to swing more than the market). "
                f"Could grow faster, but can also drop harder.")
    elif b <= 0.8 or any(k in cat for k in ["bond", "fixed income", "dividend", "value"]):
        return (f"Lower risk (tends to move less than the market). "
                f"Steadier, but probably slower growth.")
    else:
        return (f"Medium risk (moves roughly in line with the market). "
                f"A balanced middle ground.")


def full_etf_report(ticker: str) -> None:
    data = get_etf_data(ticker)

    # Skip if yfinance doesn't recognise it as a fund
    if data["expense_ratio"] is None and data["total_assets"] is None and data["top_holdings"].empty:
        return

    print(f"\n{'═'*60}")
    print(f"  ETF PROFILE  —  {ticker}")
    print(f"{'═'*60}")
    print(f"  Full name    : {data['name']}")
    print(f"  Type         : {data['category']}")

    if data["total_assets"]:
        assets_b = data["total_assets"] / 1e9
        size_note = "large, well-established fund" if assets_b > 1 else "smaller fund"
        print(f"  Fund size    : ${assets_b:.1f}B  ({size_note})")

    print(f"  Annual fee   : {fee_verdict(data['expense_ratio'])}")
    print(f"  Dividend     : {data['dividend_yield']:.2%}/yr" if data["dividend_yield"] else "  Dividend     : None / not available")
    print(f"\n  Risk summary : {risk_plain(data['beta'], data['category'])}")

    if not data["top_holdings"].empty:
        print(f"\n  What's inside (top holdings):")
        for i, row in data["top_holdings"].head(5).iterrows():
            print(f"    • {i}")

    print(f"{'═'*60}\n")



#  ACTIVITY SUMMARY  –  how much trading have you done?

def print_activity_summary(df: pd.DataFrame) -> None:
    buys  = df[df["transaction_type"] == "BUY"]
    sells = df[df["transaction_type"] == "SELL"]

    print(f"\n{'═'*60}")
    print("  YOUR TRADING HISTORY  —  At a glance")
    print(f"{'═'*60}")
    print(f"  Total buy  transactions : {len(buys)}")
    print(f"  Total sell transactions : {len(sells)}")

    if not df["trade_date"].isna().all():
        first = df["trade_date"].min().date()
        last  = df["trade_date"].max().date()
        span  = (last - first).days
        print(f"  First trade  : {first}")
        print(f"  Latest trade : {last}  ({plain_duration(span)} of history)")

    total_invested = buys["amount"].sum()
    total_proceeds = sells["amount"].sum() if len(sells) else 0
    print(f"\n  Total spent on buys  : {dollars(total_invested)}")
    if total_proceeds:
        print(f"  Total from sells     : {dollars(total_proceeds)}")
    print()


#  MAIN

if __name__ == "__main__":
    if len(sys.argv) > 1:
        PATH = sys.argv[1]
    else:
        PATH = input("Enter path to your trades CSV: ").strip().strip('"')

    print("\n  Loading your trades...")
    df = load_data(PATH)

    print_activity_summary(df)
    print_summary(df)
    print_concentration_warning(df)
    print_performance_ranking(df)

    print("\n  Checking ETF details (if any ETFs in portfolio)...\n")
    holdings    = get_holdings(df)
    etf_tickers = [f"{t}.AX" for t in holdings]
    for t in etf_tickers:
        full_etf_report(t)

    print("  Analysis complete. \n")

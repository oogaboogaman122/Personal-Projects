"""
portfolio_gui.py  —  Portfolio Analyser 
==========================================================
Run:  python portfolio_gui.py

Requires portfolio.py to be in the same folder.
Requires:  pip install pandas yfinance
"""

import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import threading
import sys
import io
import os

# make sure portfolio.py is importable from same directory 
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portfolio as p


#  COLOURS & FONTS

BG        = "#0f1117"
BG2       = "#1a1d27"
BG3       = "#22263a"
ACCENT    = "#00e5a0"       # green-mint
ACCENT2   = "#ff6b6b"       # red for losses
TEXT      = "#e8eaf0"
TEXT_DIM  = "#6b7280"
FONT_MONO = ("Courier New", 10)
FONT_UI   = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI", 13, "bold")


#  MAIN APP

class PortfolioApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Portfolio Analyser")
        self.geometry("900x700")
        self.minsize(700, 500)
        self.configure(bg=BG)
        self._csv_path = tk.StringVar(value="")
        self._build_ui()

    #UI layout 

    def _build_ui(self):
        top = tk.Frame(self, bg=BG, pady=14, padx=20)
        top.pack(fill="x")

        tk.Label(top, text="PORTFOLIO ANALYSER",
                 font=("Courier New", 14, "bold"),
                 bg=BG, fg=ACCENT).pack(side="left")

        row = tk.Frame(self, bg=BG2, padx=16, pady=12)
        row.pack(fill="x", padx=16, pady=(0, 8))

        tk.Label(row, text="Trades CSV:", font=FONT_UI,
                 bg=BG2, fg=TEXT_DIM).pack(side="left", padx=(0, 8))

        self._path_entry = tk.Entry(row, textvariable=self._csv_path,
                                    font=FONT_UI, bg=BG3, fg=TEXT,
                                    insertbackground=ACCENT,
                                    relief="flat", bd=6, width=52)
        self._path_entry.pack(side="left", padx=(0, 8))

        tk.Button(row, text="Browse…", font=FONT_UI,
                  bg=BG3, fg=ACCENT, activebackground=BG3,
                  activeforeground=ACCENT, relief="flat", bd=0,
                  cursor="hand2", padx=10,
                  command=self._browse).pack(side="left", padx=(0, 8))

        self._run_btn = tk.Button(row, text="▶  Run Analysis",
                                  font=("Segoe UI", 10, "bold"),
                                  bg=ACCENT, fg=BG,
                                  activebackground="#00c48a",
                                  activeforeground=BG,
                                  relief="flat", bd=0,
                                  cursor="hand2", padx=14, pady=4,
                                  command=self._run)
        self._run_btn.pack(side="left")

        #section tabs
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TNotebook",          background=BG,  borderwidth=0)
        style.configure("TNotebook.Tab",      background=BG3, foreground=TEXT_DIM,
                        font=FONT_UI, padding=[14, 6])
        style.map("TNotebook.Tab",
                  background=[("selected", BG2)],
                  foreground=[("selected", ACCENT)])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._tabs = {}
        for name in ("Summary", "Performance", "Spread", "ETF Details", "Full Output"):
            frame = tk.Frame(nb, bg=BG2)
            nb.add(frame, text=f"  {name}  ")
            txt = scrolledtext.ScrolledText(
                frame, font=FONT_MONO, bg=BG2, fg=TEXT,
                insertbackground=ACCENT, relief="flat",
                wrap="word", state="disabled",
                selectbackground=BG3, selectforeground=ACCENT,
                padx=14, pady=12,
            )
            txt.pack(fill="both", expand=True)
            self._tabs[name] = txt

        #status bar 
        self._status = tk.StringVar(value="Load a CSV to get started.")
        tk.Label(self, textvariable=self._status,
                 font=("Segoe UI", 9), bg=BG, fg=TEXT_DIM,
                 anchor="w", padx=20, pady=6).pack(fill="x", side="bottom")

    #actions 

    def _browse(self):
        path = filedialog.askopenfilename(
            title="Select your trades CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            self._csv_path.set(path)

    def _run(self):
        path = self._csv_path.get().strip().strip('"')
        if not path:
            self._set_status("⚠️  Please select a CSV file first.", error=True)
            return
        if not os.path.exists(path):
            self._set_status(f"⚠️  File not found: {path}", error=True)
            return

        self._run_btn.config(state="disabled", text="⏳  Analysing…")
        self._set_status("Fetching prices from Yahoo Finance — this takes ~10–20 seconds…")
        for txt in self._tabs.values():
            self._write(txt, "")

        threading.Thread(target=self._analyse, args=(path,), daemon=True).start()

    def _analyse(self, path: str):
        try:
            df = p.load_data(path)

            sections = {
                "Summary":     self._capture(p.print_summary,              df),
                "Performance": self._capture(p.print_performance_ranking,  df),
                "Spread":      self._capture(p.print_concentration_warning, df),
                "ETF Details": self._etf_section(df),
            }

            full = "\n".join(sections.values())
            sections["Full Output"] = full

            self.after(0, self._display, sections)

        except Exception as exc:
            self.after(0, self._show_error, str(exc))

    def _etf_section(self, df) -> str:
        holdings    = p.get_holdings(df)
        etf_tickers = [f"{t}.AX" for t in holdings]
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        for t in etf_tickers:
            p.full_etf_report(t)
        sys.stdout = old
        out = buf.getvalue().strip()
        return out if out else "  No ETF data found (or holdings are individual stocks)."

    def _capture(self, fn, *args) -> str:
        buf = io.StringIO()
        old = sys.stdout
        sys.stdout = buf
        fn(*args)
        sys.stdout = old
        return buf.getvalue()

    def _display(self, sections: dict):
        for tab_name, content in sections.items():
            self._write(self._tabs[tab_name], content)
        self._run_btn.config(state="normal", text="▶  Run Analysis")
        self._set_status("✅  Analysis complete.")

    def _show_error(self, msg: str):
        for txt in self._tabs.values():
            self._write(txt, f"  ❌  Error:\n\n  {msg}\n\n"
                            "  Check that your CSV has the right columns:\n"
                            "  market_code, transaction_type, instrument_code,\n"
                            "  trade_date (DD/MM/YYYY), quantity, price, amount")
        self._run_btn.config(state="normal", text="▶  Run Analysis")
        self._set_status(f"❌  Error: {msg}", error=True)

    #helpers 

    def _write(self, widget: scrolledtext.ScrolledText, text: str):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", text)
        widget.config(state="disabled")

    def _set_status(self, msg: str, error: bool = False):
        self._status.set(msg)


if __name__ == "__main__":
    app = PortfolioApp()
    app.mainloop()

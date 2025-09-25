#!/usr/bin/env python3
import matplotlib
try:
    matplotlib.use("TkAgg")  
except Exception:
    pass

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime

SHOW_PLOTS = True
START_YEAR = 2023
TICKER = "SPY"
SMA_WINDOW = 5

# Data 
def get_data(ticker="SPY", start="2023-01-01", end=None):
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)

def calculate_sma(df: pd.DataFrame, window=5) -> pd.Series:
    return df["Close"].rolling(window=window).mean()

# Upward and Downward Runs
def compute_runs(close_values: np.ndarray):
    up_runs, down_runs = [], []
    current_run = 0
    current_dir = None
    start_index = 0

    for i in range(1, len(close_values)):
        if close_values[i] > close_values[i-1]:
            if current_dir == "up":
                current_run += 1
            else:
                if current_dir == "down" and current_run > 0:
                    down_runs.append({"start": start_index, "length": current_run})
                current_dir = "up"; current_run = 1; start_index = i - 1
        elif close_values[i] < close_values[i-1]:
            if current_dir == "down":
                current_run += 1
            else:
                if current_dir == "up" and current_run > 0:
                    up_runs.append({"start": start_index, "length": current_run})
                current_dir = "down"; current_run = 1; start_index = i - 1
        else:
            if current_dir == "up" and current_run > 0:
                up_runs.append({"start": start_index, "length": current_run})
            elif current_dir == "down" and current_run > 0:
                down_runs.append({"start": start_index, "length": current_run})
            current_dir = None; current_run = 0

    if current_run > 0:
        (up_runs if current_dir == "up" else down_runs).append(
            {"start": start_index, "length": current_run}
        )
    return up_runs, down_runs

# Daily Returns 
def daily_returns(df_yr: pd.DataFrame):
    builtin = df_yr["Close"].pct_change()
    Pt = df_yr["Close"].to_numpy()
    manual = np.full_like(Pt, fill_value=np.nan, dtype=float)
    manual[1:] = (Pt[1:] - Pt[:-1]) / Pt[:-1]
    return builtin, manual

# Plots
def plot_sma(df_year: pd.DataFrame, window=SMA_WINDOW, outdir=Path("static"), ticker="SPY"):
    outdir.mkdir(parents=True, exist_ok=True)
    sma = calculate_sma(df_year, window=window)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, df_year["Close"], label="Close")
    ax.plot(df_year.index, sma, label=f"{window}-Day SMA", linestyle="--")
    year = df_year.index[0].year
    ax.set_title(f"{ticker} Close vs {window}-Day SMA ({year})")
    ax.legend()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45); plt.tight_layout()

    out_path = outdir / f"{ticker}_{year}_sma.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS: plt.show()
    plt.close(fig)

def plot_year_with_runs(df_year: pd.DataFrame, outdir=Path("static"), ticker="SPY"):
    from matplotlib import patheffects as pe

    outdir.mkdir(parents=True, exist_ok=True)
    close = df_year["Close"].to_numpy()
    up_runs, down_runs = compute_runs(close)

    colors = ["green" if close[i] > close[i-1] else "red" if close[i] < close[i-1] else "gray"
              for i in range(1, len(close))]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, close, color="black", linewidth=1, label="Close")

    for i in range(1, len(close)):
        ax.plot(df_year.index[i-1:i+1], close[i-1:i+1],
                color=colors[i-1], linewidth=1.5, alpha=0.8)

    def bold_line(x, y, color, label):
        line, = ax.plot(x, y, color=color, linewidth=4.5, alpha=1.0, zorder=5, label=label)
        line.set_path_effects([pe.Stroke(linewidth=7.5, foreground="white", alpha=0.9), pe.Normal()])
        return line

    if up_runs:
        up_run = max(up_runs, key=lambda r: r["length"])
        s, e = up_run["start"], up_run["start"] + up_run["length"]
        bold_line(df_year.index[s:e+1], close[s:e+1], "green",
                  f"Longest Up ({up_run['length']} days)")
        ax.text(df_year.index[e], close[e],
                f"Longest Up ({up_run['length']}d)",
                color="green", fontsize=10, fontweight="bold",
                ha="left", va="bottom",
                path_effects=[pe.Stroke(linewidth=3, foreground="white"), pe.Normal()])

    if down_runs:
        down_run = max(down_runs, key=lambda r: r["length"])
        s, e = down_run["start"], down_run["start"] + down_run["length"]
        bold_line(df_year.index[s:e+1], close[s:e+1], "red",
                  f"Longest Down ({down_run['length']} days)")
        ax.text(df_year.index[e], close[e],
                f"Longest Down ({down_run['length']}d)",  
                color="red", fontsize=10, fontweight="bold",
                ha="left", va="top",
                path_effects=[pe.Stroke(linewidth=3, foreground="white"), pe.Normal()])

    year = df_year.index[0].year
    ax.set_title(f"{ticker} Closing Price with Runs ({year})")
    ax.legend()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45); plt.tight_layout()

    out_path = outdir / f"{ticker}_{year}_runs.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS: plt.show()
    plt.close(fig)

#  Main
def main():
    start_date = f"{START_YEAR}-01-01"
    data = get_data(ticker=TICKER, start=start_date, end=None)
    if data.empty:
        print("No data found."); return

    print(f"Pulled {len(data)} rows for {TICKER} (since {START_YEAR}).")

    # Daily Returns
    builtin_ret, manual_ret = daily_returns(data)
    print("\nDaily returns (pandas head):")
    print(builtin_ret.head(10))
    print("\nDaily returns (manual head):")
    print(manual_ret[:10])

    # Per-year Plots
    current_year = datetime.now().year
    for yr in range(START_YEAR, current_year + 1):
        df_year = data[data.index.year == yr]
        if df_year.empty: continue
        plot_sma(df_year, window=SMA_WINDOW, ticker=TICKER)
        plot_year_with_runs(df_year, ticker=TICKER)

if __name__ == "__main__":
    main()
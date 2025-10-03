#!/usr/bin/env python3
# Visualisation.py
'''Visualization helpers for financial time series.

This module contains functions to fetch price history and produce plots:
- plot_sma: saves a chart of Close price with a simple moving average (SMA).
- compute_runs / plot_runs: detect streaks of consecutive up/down days and
    visualize the longest runs.

The scripts use yfinance to fetch data and matplotlib for plotting.
'''
import matplotlib
try:
    matplotlib.use("TkAgg")  
except Exception:
    pass

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import patheffects as pe
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path
from datetime import datetime
import sys

TICKER = "SPY"
START = "2023-01-01"
DEFAULT_SMA_WINDOW = 5
SHOW_PLOTS = True  

# Data  
def get_data(ticker=TICKER, start=START, end=None) -> pd.DataFrame:
    """Fetch historical OHLCV data for a ticker using yfinance.

    Parameters
    ----------
    ticker : str
        Ticker symbol to fetch. Defaults to module-level TICKER.
    start : str
        Start date (YYYY-MM-DD).
    end : str | None
        Optional end date.

    Returns
    -------
    pd.DataFrame
        OHLCV history with DatetimeIndex.
    """
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)

def calculate_sma(df: pd.DataFrame, window=DEFAULT_SMA_WINDOW) -> pd.Series:
    """Calculate a simple moving average (SMA) of the Close price.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe that contains a "Close" column.
    window : int
        Rolling window size in trading days.

    Returns
    -------
    pd.Series
        SMA values aligned with the input index.
    """
    return df["Close"].rolling(window=window).mean()

# Upward and Downward Runs
def compute_runs(close_values: np.ndarray):
    """Return up_runs, down_runs as list[{'start': i, 'length': k}] (k = steps)."""
    """Compute contiguous runs of increasing or decreasing close prices.

    Parameters
    ----------
    close_values : np.ndarray
        1-D array of close prices.

    Returns
    -------
    tuple[list[dict], list[dict]]
        Two lists describing up runs and down runs. Each run is a dict with
        keys 'start' (index of first day in run) and 'length' (number of steps).
    """
    up_runs, down_runs = [], []
    cur_len, cur_dir, start_idx = 0, None, 0
    for i in range(1, len(close_values)):
        if close_values[i] > close_values[i-1]:         
            if cur_dir == "up":
                cur_len += 1
            else:
                if cur_dir == "down" and cur_len > 0:
                    down_runs.append({"start": start_idx, "length": cur_len})
                cur_dir, cur_len, start_idx = "up", 1, i - 1
        elif close_values[i] < close_values[i-1]:       
            if cur_dir == "down":
                cur_len += 1
            else:
                if cur_dir == "up" and cur_len > 0:
                    up_runs.append({"start": start_idx, "length": cur_len})
                cur_dir, cur_len, start_idx = "down", 1, i - 1
        else:                                           
            if cur_dir == "up" and cur_len > 0:
                up_runs.append({"start": start_idx, "length": cur_len})
            elif cur_dir == "down" and cur_len > 0:
                down_runs.append({"start": start_idx, "length": cur_len})
            cur_dir, cur_len = None, 0
    if cur_len > 0:
        (up_runs if cur_dir == "up" else down_runs).append(
            {"start": start_idx, "length": cur_len}
        )
    return up_runs, down_runs

# Plotting SMA
def plot_sma(df_year: pd.DataFrame, ticker=TICKER, window=DEFAULT_SMA_WINDOW, outdir=Path("static")):
    """Plot Close price and SMA for a single year and save to a file.

    Parameters
    ----------
    df_year : pd.DataFrame
        Data containing rows for a single year (DatetimeIndex expected).
    ticker : str
        Symbol for titles and filenames.
    window : int
        SMA window in days.
    outdir : Path
        Directory where the resulting PNG will be saved.

    Returns
    -------
    Path
        Path to the saved PNG file.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    sma = calculate_sma(df_year, window)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, df_year["Close"], label="Close")
    ax.plot(df_year.index, sma, label=f"{window}-Day SMA", linestyle="--")
    year = df_year.index[0].year
    ax.set_title(f"{ticker} Close vs {window}-Day SMA ({year})")
    ax.legend()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    out_path = outdir / f"{ticker}_{year}_sma_{window}.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS: plt.show()
    plt.close(fig)
    return out_path

# Plotting Runs
def plot_runs(df_year: pd.DataFrame, ticker=TICKER, outdir=Path("static")):
    """Plot daily close prices with visual emphasis on up/down runs.

    The function highlights the longest consecutive up and down runs and saves
    the figure as a PNG in the given output directory.

    Parameters
    ----------
    df_year : pd.DataFrame
        Data for a single year (DatetimeIndex expected).
    ticker : str
        Symbol used for titles and filenames.
    outdir : Path
        Directory to save the PNG.

    Returns
    -------
    Path
        Path to the saved PNG file.
    """
    outdir.mkdir(parents=True, exist_ok=True)
    close = df_year["Close"].to_numpy()
    up_runs, down_runs = compute_runs(close)

    colors = ["green" if close[i] > close[i-1]
              else "red" if close[i] < close[i-1] else "gray"
              for i in range(1, len(close))]

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, close, color="black", linewidth=1, label="Close")

    for i in range(1, len(close)):
        ax.plot(df_year.index[i-1:i+1], close[i-1:i+1],
                color=colors[i-1], linewidth=1.5, alpha=0.8)

    def bold_line(x, y, color, label):
        line, = ax.plot(x, y, color=color, linewidth=4.5, zorder=5, label=label)
        line.set_path_effects([
            pe.Stroke(linewidth=7.5, foreground="white", alpha=0.9),
            pe.Normal()
        ])
        return line

    if up_runs:
        u = max(up_runs, key=lambda r: r["length"])
        s, e = u["start"], u["start"] + u["length"]
        bold_line(df_year.index[s:e+1], close[s:e+1], "green",
                  f"Longest Up ({u['length']} days)")
        ax.text(df_year.index[e], close[e], f"Longest Up ({u['length']}d)",
                color="green", fontsize=10, fontweight="bold",
                ha="left", va="bottom",
                path_effects=[pe.Stroke(linewidth=3, foreground="white"), pe.Normal()])

    if down_runs:
        d = max(down_runs, key=lambda r: r["length"])
        s, e = d["start"], d["start"] + d["length"]
        bold_line(df_year.index[s:e+1], close[s:e+1], "red",
                  f"Longest Down ({d['length']} days)")
        ax.text(df_year.index[e], close[e], f"Longest Down ({d['length']}d)",
                color="red", fontsize=10, fontweight="bold",
                ha="left", va="top",
                path_effects=[pe.Stroke(linewidth=3, foreground="white"), pe.Normal()])

    year = df_year.index[0].year
    ax.set_title(f"{ticker} Closing Price with Runs ({year})")
    ax.legend()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)
    plt.tight_layout()
    out_path = outdir / f"{ticker}_{year}_runs.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS: plt.show()
    plt.close(fig)
    return out_path

# Main
def main():
    if len(sys.argv) > 1:
        try:
            sma_window = int(sys.argv[1])
        except ValueError:
            print("Invalid SMA window in argument, will ask interactively.")
            sma_window = None
    else:
        sma_window = None

    if sma_window is None:
        user_in = input(f"Enter SMA window (default={DEFAULT_SMA_WINDOW}): ").strip()
        if user_in.isdigit():
            sma_window = int(user_in)
        else:
            sma_window = DEFAULT_SMA_WINDOW

    df = get_data()
    if df.empty:
        print("No data returned."); return

    current_year = datetime.now().year
    for yr in range(pd.Timestamp(START).year, current_year + 1):
        df_year = df[df.index.year == yr]
        if df_year.empty:
            continue
        p1 = plot_sma(df_year, ticker=TICKER, window=sma_window)
        p2 = plot_runs(df_year, ticker=TICKER)
        print(f"Saved: {p1}\nSaved: {p2}")

if __name__ == "__main__":
    main()
    

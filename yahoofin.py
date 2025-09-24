import os, sys, platform, subprocess, webbrowser
import matplotlib
try:
    matplotlib.use("TkAgg")  
except Exception as e:
    print("Could not set GUI backend (TkAgg):", e)
if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
    print("Warning: no DISPLAY detected; GUI windows may not open (headless).")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path

SHOW_PLOTS = True  

def open_file(path: str):
    try:
        if platform.system() == "Windows":
            os.startfile(path)  
        elif platform.system() == "Darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        webbrowser.open(f"file://{os.path.abspath(path)}")


def get_data(ticker="SPY", start="2023-01-01", end=None):
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)

def filter_years(df: pd.DataFrame, years=(2023, 2024)) -> pd.DataFrame:
    return df[df.index.year.isin(years)].copy()

def calculate_sma(df: pd.DataFrame, window=5) -> pd.Series:
    return df["Close"].rolling(window=window).mean()


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
                current_dir = "up"
                current_run = 1
                start_index = i - 1
        elif close_values[i] < close_values[i-1]:
            if current_dir == "down":
                current_run += 1
            else:
                if current_dir == "up" and current_run > 0:
                    up_runs.append({"start": start_index, "length": current_run})
                current_dir = "down"
                current_run = 1
                start_index = i - 1
        else:
            if current_dir == "up" and current_run > 0:
                up_runs.append({"start": start_index, "length": current_run})
            elif current_dir == "down" and current_run > 0:
                down_runs.append({"start": start_index, "length": current_run})
            current_dir = None
            current_run = 0

    if current_run > 0:
        if current_dir == "up":
            up_runs.append({"start": start_index, "length": current_run})
        elif current_dir == "down":
            down_runs.append({"start": start_index, "length": current_run})

    return up_runs, down_runs

def summarize_runs(close_vals: np.ndarray):
    up_runs, down_runs = compute_runs(close_vals)
    up_count, down_count = len(up_runs), len(down_runs)
    longest_up = max(up_runs, key=lambda r: r["length"]) if up_runs else None
    longest_down = max(down_runs, key=lambda r: r["length"]) if down_runs else None
    return {
        "up_runs": up_runs, "down_runs": down_runs,
        "up_count": up_count, "down_count": down_count,
        "longest_up": longest_up, "longest_down": longest_down
    }

def daily_returns(df_yr: pd.DataFrame):
    builtin = df_yr["Close"].pct_change()
    Pt = df_yr["Close"].to_numpy()
    manual = np.full_like(Pt, fill_value=np.nan, dtype=float)
    manual[1:] = (Pt[1:] - Pt[:-1]) / Pt[:-1]
    return builtin, manual

def max_profit_multiple(prices: np.ndarray) -> float:
    return float(np.maximum(prices[1:] - prices[:-1], 0).sum())

def best_time_to_buy_sell(prices: np.ndarray):
    n, i = len(prices), 0
    tx = []
    while i < n - 1:
        while i < n - 1 and prices[i+1] <= prices[i]:
            i += 1
        if i == n - 1:
            break
        buy = i
        i += 1
        while i < n and (i == n - 1 or prices[i] >= prices[i-1]):
            if i == n - 1 or prices[i+1] < prices[i]:
                sell = i
                tx.append((buy, sell))
                break
            i += 1
    return tx

def plot_year_with_runs(df_year: pd.DataFrame, outdir=Path("static"), ticker="SPY"):
    from matplotlib import patheffects as pe

    outdir.mkdir(parents=True, exist_ok=True)
    close = df_year["Close"].to_numpy()
    up_runs, down_runs = compute_runs(close)

    colors = []
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            colors.append("green")
        elif close[i] < close[i-1]:
            colors.append("red")
        else:
            colors.append("gray")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, close, color="black", linewidth=1, label="Close", alpha=0.9)

    for i in range(1, len(close)):
        ax.plot(df_year.index[i-1:i+1], close[i-1:i+1],
                color=colors[i-1], linewidth=1.5, alpha=0.8)

    def bold_line(x, y, color, label):
        line, = ax.plot(x, y, color=color, linewidth=4.5, alpha=1.0, zorder=5, label=label)
        line.set_path_effects([
            pe.Stroke(linewidth=7.5, foreground="white", alpha=0.9),
            pe.Normal()
        ])
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
    ax.set_title(f"{ticker} Closing Price with Up/Down Runs ({year})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(frameon=True)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    out_path = outdir / f"{ticker}_{year}_runs.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS:
        try:
            plt.show()
        except Exception as e:
            print("Could not show() GUI window:", e)
            open_file(str(out_path))
    plt.close(fig)
    return out_path

def plot_sma(df_year: pd.DataFrame, window=5, outdir=Path("static"), ticker="SPY"):
    outdir.mkdir(parents=True, exist_ok=True)
    sma = calculate_sma(df_year, window=window)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, df_year["Close"], label="Close")
    ax.plot(df_year.index, sma, label=f"{window}-Day SMA", linestyle="--")
    year = df_year.index[0].year
    ax.set_title(f"{ticker} Close vs {window}-Day SMA ({year})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    out_path = outdir / f"{ticker}_{year}_sma.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS:
        try:
            plt.show()
        except Exception as e:
            print("Could not show() GUI window:", e)
            open_file(str(out_path))
    plt.close(fig)
    return out_path


def main():
    ticker = "SPY"
    years = (2023, 2024)

    data = get_data(ticker=ticker, start="2023-01-01")
    data_years = filter_years(data, years)
    if data_years.empty:
        print(f"No data for {ticker} within {years}.")
        return

    print(f"Pulled {len(data)} rows; filtered to {len(data_years)} rows for years {years}")

    # Daily returns 
    builtin_ret, manual_ret = daily_returns(data_years)
    print("\nDaily returns (pandas head):")
    print(builtin_ret.head(10))
    print("\nDaily returns (manual head):")
    print(manual_ret[:10])

    # Up/Down runs summary 
    close_vals = data_years["Close"].to_numpy()
    runs = summarize_runs(close_vals)
    print(f"\nUpward runs: {runs['up_count']}")
    print(f"Downward runs: {runs['down_count']}")
    if runs["longest_up"]:
        lu = runs["longest_up"]
        print(f"Longest upward streak: {lu['length']} days (start idx {lu['start']})")
    else:
        print("Longest upward streak: N/A")
    if runs["longest_down"]:
        ld = runs["longest_down"]
        print(f"Longest downward streak: {ld['length']} days (start idx {ld['start']})")
    else:
        print("Longest downward streak: N/A")

    # Max profit & explicit transactions
    profit = max_profit_multiple(close_vals)
    print(f"\nMax profit (multiple transactions) for {years}: {profit:.2f}")
    tx = best_time_to_buy_sell(close_vals)
    if tx:
        for i, (b, s) in enumerate(tx, start=1):
            pnl = close_vals[s] - close_vals[b]
            print(f"Transaction {i}: Buy idx {b}, Sell idx {s}, Profit: {pnl:.2f}")
    else:
        print("No profitable transactions found.")

    # Average close
    avg_close = float(data_years["Close"].mean())
    print(f"\nAverage closing price for {ticker} in {years}: {avg_close:.2f}")

    # Per-year charts
    for yr in years:
        df_year = data[data.index.year == yr].copy()
        if df_year.empty:
            print(f"Warning: no data for {yr}")
            continue
        sma_path = plot_sma(df_year, window=5, ticker=ticker)
        runs_path = plot_year_with_runs(df_year, ticker=ticker)
        print(f"Saved: {sma_path}")
        print(f"Saved: {runs_path}")

if __name__ == "__main__":
    print("Matplotlib backend:", matplotlib.get_backend())
    main()

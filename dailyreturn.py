#!/usr/bin/env python3
# daily_returns.py
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

START_YEAR = 2023
TICKER = "SPY"

def get_data(ticker=TICKER, start=f"{START_YEAR}-01-01", end=None) -> pd.DataFrame:
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)

def compute_daily_returns(df: pd.DataFrame):
    builtin = df["Close"].pct_change()
    pt = df["Close"].to_numpy()
    manual = np.full_like(pt, np.nan, dtype=float)
    if len(pt) > 1:
        manual[1:] = (pt[1:] - pt[:-1]) / pt[:-1]
    return builtin, manual

def main():
    df = get_data()
    if df.empty:
        print("No data returned."); return
    builtin, manual = compute_daily_returns(df)

    print(f"Rows pulled: {len(df)} for {TICKER} (since {START_YEAR})")
    print("\nDaily returns (pandas head):")
    print(builtin.head(10))
    print("\nDaily returns (manual head):")
    print(manual[:10])

if __name__ == "__main__":
    main()
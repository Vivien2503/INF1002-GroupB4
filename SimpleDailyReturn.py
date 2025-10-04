#!/usr/bin/env python3
# SimpleDailyReturn.py
"""
Fetch historical prices and compute simple daily returns.
Supports both CLI (multi-ticker) and Flask integration.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime


def get_data(ticker: str, start="2023-01-01", end=None) -> pd.DataFrame:
    """Return OHLCV history for a ticker (yfinance)."""
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)


def compute_daily_returns(df: pd.DataFrame):
    """Return (pandas_pct_change, manual_numpy_array) of Close returns."""
    builtin = df["Close"].pct_change()
    pt = df["Close"].to_numpy()
    manual = np.full_like(pt, np.nan, dtype=float)
    if len(pt) > 1:
        manual[1:] = (pt[1:] - pt[:-1]) / pt[:-1]
    return builtin, manual


def get_daily_return_analysis(tickers="SPY", target_dates=None, start="2023-01-01", end=None):
    """Flask-ready: return list of dicts with close price and daily returns."""
    results = []
    try:
        # Normalize inputs
        if isinstance(tickers, str):
            tickers = [tickers]
        if isinstance(target_dates, str):
            target_dates = [target_dates]

        if not tickers or not target_dates:
            return results

        for ticker in tickers:
            df = get_data(ticker=ticker, start=start, end=end)
            if df.empty:
                continue

            builtin, manual = compute_daily_returns(df)
            df["BuiltinReturn"] = builtin * 100
            df["ManualReturn"] = manual * 100
            df.index = df.index.date

            for target_date in target_dates:
                try:
                    user_date = datetime.strptime(target_date, "%Y-%m-%d").date()
                except ValueError:
                    continue

                if user_date not in df.index:
                    continue

                row = df.loc[user_date]
                results.append({
                    "ticker": ticker,
                    "date": target_date,
                    "close_price": round(float(row['Close']), 2),
                    "builtin_return": round(float(row['BuiltinReturn']), 2),
                    "manual_return": round(float(row['ManualReturn']), 2)
                })
    except Exception:
        return []

    return results


def main():
    """CLI: prompt for tickers and date, then print daily returns."""
    # Ask user to input tickers
    tickers_str = input("Enter ticker symbols separated by commas (e.g. SPY,AAPL,MSFT): ").strip()
    tickers = [t.strip().upper() for t in tickers_str.split(",") if t.strip()]

    if not tickers:
        print("No tickers provided.")
        return

    # Ask user for a date
    user_date_str = input("Enter a date (YYYY-MM-DD): ").strip()
    try:
        user_date = datetime.strptime(user_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Loop through all user-provided tickers
    for ticker in tickers:
        df = get_data(ticker)
        if df.empty:
            print(f"No data returned for {ticker}.")
            continue

        builtin, manual = compute_daily_returns(df)
        df["BuiltinReturn"] = builtin * 100
        df["ManualReturn"] = manual * 100
        df.index = df.index.date

        if user_date not in df.index:
            print(f"No trading data for {ticker} on {user_date} (market closed or holiday).")
            continue

        row = df.loc[user_date]
        print(f"\nTicker: {ticker}")
        print(f"Date: {user_date}")
        print(f"Close Price: {row['Close']:.2f}")
        print(f"Daily Return (pandas): {row['BuiltinReturn']:.2f}%")
        print(f"Daily Return (manual): {row['ManualReturn']:.2f}%")


if __name__ == "__main__":
    main()
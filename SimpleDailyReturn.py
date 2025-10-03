#!/usr/bin/env python3
# SimpleDailyReturn.py
'''Utility to fetch historical price data and compute simple daily returns.

This module provides:
- get_data: fetches OHLCV data for a ticker using yfinance.
- compute_daily_returns: compares pandas pct_change with manual numpy calculation.
- main: simple CLI to query tickers and print returns for a specified date.

Dependencies: numpy, pandas, yfinance
'''
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

def get_data(ticker: str, start="2023-01-01", end=None) -> pd.DataFrame:
    """Fetch historical market data for a ticker from Yahoo Finance.

    Parameters
    ----------
    ticker : str
        Stock/ETF symbol, e.g. "SPY" or "AAPL".
    start : str
        Start date in "YYYY-MM-DD" format. Defaults to "2023-01-01".
    end : str | None
        End date in "YYYY-MM-DD" format. If None, fetches up through latest available.

    Returns
    -------
    pd.DataFrame
        OHLCV history with a DatetimeIndex (timezone-aware).
    """
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)

def compute_daily_returns(df: pd.DataFrame):
    """Compute daily simple returns two ways: pandas' pct_change and a manual numpy method.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing at least a "Close" column.

    Returns
    -------
    tuple[pd.Series, np.ndarray]
        (builtin_returns, manual_returns) where builtin_returns is the pandas
        percent-change Series and manual_returns is a numpy array of the same
        length (first element is NaN).
    """
    builtin = df["Close"].pct_change()
    pt = df["Close"].to_numpy()
    manual = np.full_like(pt, np.nan, dtype=float)
    if len(pt) > 1:
        manual[1:] = (pt[1:] - pt[:-1]) / pt[:-1]
    return builtin, manual

def main():
    """Command line entrypoint.

    Interactively asks the user for ticker symbols and a date, fetches data,
    computes daily returns, and prints the close price and returns for the
    requested date. Intended for quick local use and demonstrations.
    """
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
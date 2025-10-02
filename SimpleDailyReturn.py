#!/usr/bin/env python3
# SimpleDailyReturn.py
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

TICKER = "SPY"

def get_data(ticker=TICKER, start="2023-01-01", end=None) -> pd.DataFrame:
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)

def compute_daily_returns(df: pd.DataFrame):
    builtin = df["Close"].pct_change()
    pt = df["Close"].to_numpy()
    manual = np.full_like(pt, np.nan, dtype=float)
    if len(pt) > 1:
        manual[1:] = (pt[1:] - pt[:-1]) / pt[:-1]
    return builtin, manual

def get_daily_return_analysis(ticker="SPY", target_date=None, start="2023-01-01", end=None):
    """
    Function to get daily return analysis that can be called from Flask app.
    Returns: dict with daily return data or None if unavailable
    """
    try:
        if target_date is None:
            return None
            
        # Parse target date
        user_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        # Fetch data
        df = get_data(ticker=ticker, start=start, end=end)
        if df.empty:
            return None

        builtin, manual = compute_daily_returns(df)
        df["BuiltinReturn"] = builtin * 100  
        df["ManualReturn"] = manual * 100    
        df.index = df.index.date

        if user_date not in df.index:
            return None

        row = df.loc[user_date]
        return {
            "ticker": ticker,
            "date": target_date,
            "close_price": round(float(row['Close']), 2),
            "builtin_return": round(float(row['BuiltinReturn']), 2),
            "manual_return": round(float(row['ManualReturn']), 2)
        }
    except Exception:
        return None

def main():
    # Get user to input date
    user_date_str = input("Enter a date (YYYY-MM-DD): ").strip()
    try:
        user_date = datetime.strptime(user_date_str, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return

    # Fetch data from 2023 up to today
    df = get_data()
    if df.empty:
        print("No data returned.")
        return

    builtin, manual = compute_daily_returns(df)
    df["BuiltinReturn"] = builtin * 100  
    df["ManualReturn"] = manual * 100    
    
    df.index = df.index.date

    if user_date not in df.index:
        print(f"No trading data for {user_date} (market closed or holiday).")
        return

    row = df.loc[user_date]
    print(f"\nTicker: {TICKER}")
    print(f"Date: {user_date}")
    print(f"Close Price: {row['Close']:.2f}")
    print(f"Daily Return (pandas): {row['BuiltinReturn']:.2f}%")
    print(f"Daily Return (manual): {row['ManualReturn']:.2f}%")

if __name__ == "__main__":
    main()

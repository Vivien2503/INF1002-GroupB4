import yfinance as yf
import pandas as pd
import os
from datetime import date

def get_sma_for_date(
    ticker="SPY",
    start="2023-01-01",
    end=None,
    period=30,
    target_date=None,
    snap_to_previous=True,  # snap non-trading days to the nearest previous trading day
    save_to_csv=False,
    csv_filename="sma_values.csv"
):
    """
    Computes SMA and prints the SMA value for a specific date.

    Parameters:
    ticker (str): Stock/ETF symbol (default = 'SPY')
    start (str): Start date for data (YYYY-MM-DD)
    end (str): End date for data (YYYY-MM-DD). Defaults to today if None.
    period (int): SMA window length (default = 30 days)
    target_date (str): Date (YYYY-MM-DD) to show SMA for
    snap_to_previous (bool): If True, use previous trading day if target_date not available
    save_to_csv (bool): If True, saves SMA values to a CSV file
    csv_filename (str): Name of CSV file if saving

    Returns:
    float: SMA value for the date (or None if unavailable)
    """
    if end is None:
        end = date.today().isoformat()

    # 1. Download data
    data = yf.download(ticker, start=start, end=end, progress=False)
    if data.empty:
        print("No data found for the given parameters.")
        return None

    # 2. Compute SMA
    data['SMA'] = data['Close'].rolling(window=period, min_periods=1).mean()

    # 3. Find SMA for the target date
    idx = pd.to_datetime(target_date)
    if idx not in data.index:
        if snap_to_previous:
            prev_idx = data.index[data.index <= idx].max()
            if pd.isna(prev_idx):
                print(f"No trading data available on or before {target_date}.")
                return None
            else:
                sma_value = float(data.loc[prev_idx, 'SMA'])
                print(f"\nRequested {target_date} (non-trading). Nearest trading day: {prev_idx.date()}")
                print(f"SMA on {prev_idx.date()} ({period}-day): {sma_value:.2f}")
                return sma_value
        else:
            print(f"No trading data for {target_date}.")
            return None
    else:
        sma_value = float(data.loc[idx, 'SMA'])
        print(f"\nSMA on {target_date} ({period}-day): {sma_value:.2f}")
        return sma_value

    # 4. Optionally save all SMA values
    if save_to_csv:
        data['SMA'].to_csv(csv_filename)
        print(f"SMA values saved to {os.path.abspath(csv_filename)}")


# Example usage
if __name__ == "__main__":
    ticker = input("Enter stock ticker: ")
    sma_days = int(input("Enter SMA period: "))
    user_date = input("Enter the date (YYYY-MM-DD): ")

    get_sma_for_date(
        ticker=ticker,
        start="2023-01-01",
        period=sma_days,
        target_date=user_date
    )

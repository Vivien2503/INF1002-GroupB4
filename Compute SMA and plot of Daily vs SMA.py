import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import os
from datetime import date

def plot_closing_vs_sma(
    ticker="SPY",
    start="2023-01-01",
    end=None,
    period=30,
    save_to_csv=False,
    csv_filename="sma_values.csv",
    target_date=None,
    snap_to_previous=True   # snap non-trading days to the nearest previous trading day
):
    """
    Plots the Closing Price vs SMA and prints the SMA value for a specific date.

    Parameters:
    ticker (str): Stock/ETF symbol (default = 'SPY')
    start (str): Start date (YYYY-MM-DD)
    end (str): End date (YYYY-MM-DD). Defaults to today if None.
    period (int): SMA window length (default = 30 days)
    save_to_csv (bool): If True, saves SMA values to a CSV file
    csv_filename (str): Name of CSV file if saving
    target_date (str): Date (YYYY-MM-DD) to show SMA for
    snap_to_previous (bool): If True, use previous trading day if target_date not available

    Returns:
    pd.Series: SMA values
    """
    if end is None:
        end = date.today().isoformat()

    # 1. Download data
    data = yf.download(ticker, start=start, end=end, progress=False)
    print(f"Number of data points: {len(data)}")
    if data.empty:
        print("No data found for the given parameters.")
        return None

    # 2. Compute SMA
    data['SMA'] = data['Close'].rolling(window=period, min_periods=1).mean()

    # 3. Plot Closing Price vs SMA
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data['Close'], label="Daily Closing Price", color='blue')
    plt.plot(data.index, data['SMA'], label=f"{period}-Day SMA", color='orange', linestyle='--', linewidth=2)
    plt.title(f"{ticker} Closing Price vs {period}-Day SMA")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 4. Print SMA value for target_date
    if target_date:
        idx = pd.to_datetime(target_date)

        if idx not in data.index:
            if snap_to_previous:
                prev_idx = data.index[data.index <= idx].max()
                if pd.isna(prev_idx):
                    print(f"\nNo trading data available on or before {target_date}.")
                else:
                    sma_value = float(data.loc[prev_idx, 'SMA'])
                    print(f"\nRequested {target_date} (non-trading). Nearest trading day: {prev_idx.date()}")
                    print(f"SMA on {prev_idx.date()}: {sma_value:.2f}")
            else:
                print(f"\nNo trading data for {target_date}.")
        else:
            sma_value = float(data.loc[idx, 'SMA'])
            print(f"\nSMA on {target_date}: {sma_value:.2f}")
    else:
        print("\nSMA Values:")
        print(data['SMA'])

    # 5. Optionally save all SMA values to CSV
    if save_to_csv:
        data['SMA'].to_csv(csv_filename)
        print(f"\nSMA values saved to {os.path.abspath(csv_filename)}")

    return data['SMA']


# Example usage
if __name__ == "__main__":
    sma_values = plot_closing_vs_sma(
        ticker="SPY",
        start="2023-01-01",
        period=30,
        save_to_csv=False,
        csv_filename="spy_sma.csv",
        target_date="2023-05-15"  # <-- *** To pick the date you want to check ***
    )

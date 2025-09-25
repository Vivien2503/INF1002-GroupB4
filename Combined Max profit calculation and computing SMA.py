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


    # --- Max Profit Calculation ---

# Best Time to Buy and Sell Stock II (multiple transactions allowed)

import yfinance as yf

def max_profit_multiple(prices):
    """
    Return the maximum profit when multiple buy/sell transactions are allowed.
    prices: list of daily prices
    """
    profit = 0.0
    for i in range(1, len(prices)):
        gain = prices[i] - prices[i - 1]
        if gain > 0:
            profit += gain
    return profit

def extract_trades(prices):
    """
    Return a list of (buy_index, sell_index) pairs that achieve the same max profit.
    """
    trades = []
    i, n = 0, len(prices)
    while i < n - 1:
        # find local minimum (buy)
        while i < n - 1 and prices[i + 1] <= prices[i]:
            i += 1
        buy = i

        # find local maximum (sell)
        while i < n - 1 and prices[i + 1] >= prices[i]:
            i += 1
        sell = i

        if sell > buy:
            trades.append((buy, sell))
        i += 1
    return trades

if __name__ == "__main__":
    # --- Example with a small list ---
    prices = [7, 1, 5, 3, 6, 4]
    profit = max_profit_multiple(prices)
    trades = extract_trades(prices)
    print("Example prices:", prices)
    print("Max Profit:", profit)
    print("Trades (buy,sell indices):", trades)

    # --- Example with real S&P 500 ETF (SPY) data ---
    data = yf.download("SPY", start="2023-01-01", end=None, progress=False)
    if "Close" not in data.columns or data["Close"].empty:
        print("No 'Close' price data found for SPY in the given range.")
    else:
        closes = data["Close"].squeeze().astype(float).tolist()
        profit_spy = max_profit_multiple(closes)
        trades_spy = extract_trades(closes)
        print("\nSPY from 2023 to now:")
        print("Max Profit:", profit_spy)
        print("Number of trades:", len(trades_spy))
        # Print actual buy/sell dates and prices
        for buy_idx, sell_idx in trades_spy:
            buy_date = data.index[buy_idx].date()
            sell_date = data.index[sell_idx].date()
            buy_price = closes[buy_idx]
            sell_price = closes[sell_idx]
            print(f"Buy on {buy_date} at {buy_price:.2f}, Sell on {sell_date} at {sell_price:.2f}")

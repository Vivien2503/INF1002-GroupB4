import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

def plot_closing_vs_sma(ticker="SPY", start="2023-01-01", end=None, period=30):
    """
    Plots the daily closing price against the Simple Moving Average (SMA).

    Parameters:
    ticker (str): Stock/ETF symbol (default = 'SPY' for S&P 500 ETF)
    start (str): Start date for the data (YYYY-MM-DD)
    end (str): End date for the data (YYYY-MM-DD)
    period (int): Window length for SMA (default = 30 days)
    """

    # 1. Download data
    data = yf.download(ticker, start=start, end=end)
    print(f"Number of data points: {len(data)}")
    if data.empty:
        print("No data found for the given parameters.")
        return

    # 2. Ensure we use the 'Close' column
    data['SMA'] = data['Close'].rolling(window=period, min_periods=1).mean()

    # 3. Plot Closing Price vs SMA
    plt.figure(figsize=(12,6))
    plt.plot(data.index, data['Close'], label="Daily Closing Price", color='blue')
    plt.plot(data.index, data['SMA'], label=f"{period}-Day SMA", color='orange', linestyle='--', linewidth=2)

    # 4. Title, labels, legend
    plt.title(f"{ticker} Daily Closing Price vs {period}-Day SMA")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()

# Run the function when the script is executed
if __name__ == "__main__":
    plot_closing_vs_sma(ticker="SPY", start="2022-01-01", end=None, period=30)

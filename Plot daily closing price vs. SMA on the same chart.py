import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd

def plot_closing_vs_sma(
    ticker="SPY", 
    start="2023-01-01", 
    end=None, 
    period=30,
    save_to_csv=False, 
    csv_filename="sma_values.csv"
):
    """
    Plots the daily closing price against the Simple Moving Average (SMA).
    Prints SMA values only in the terminal, and optionally saves them to CSV.

    Parameters:
    ticker (str): Stock/ETF symbol (default = 'SPY')
    start (str): Start date for the data (YYYY-MM-DD)
    end (str): End date for the data (YYYY-MM-DD)
    period (int): Window length for SMA (default = 30 days)
    save_to_csv (bool): If True, saves SMA values to CSV
    csv_filename (str): File name for CSV output

    Returns:
    pd.Series: SMA values
    """

    # 1. Download data
    data = yf.download(ticker, start=start, end=end)
    print(f"Number of data points: {len(data)}")
    if data.empty:
        print("No data found for the given parameters.")
        return None

    # 2. Computing the SMA
    data['SMA'] = data['Close'].rolling(window=period, min_periods=1).mean()

    # 3. Plot Closing Price vs SMA
    plt.figure(figsize=(12,6))
    plt.plot(data.index, data['Close'], label="Daily Closing Price", color='blue')
    plt.plot(data.index, data['SMA'], label=f"{period}-Day SMA", color='orange', linestyle='--', linewidth=2)
    plt.title(f"{ticker} Daily Closing Price vs {period}-Day SMA")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # 4. Print only SMA values in terminal
    print("\nSMA Values:")
    print(data['SMA'])

    # 5. Optionally save to CSV
    if save_to_csv:
        data['SMA'].to_csv(csv_filename)
        print(f"\nSMA values saved to {csv_filename}")

    # 6. Return SMA series
    return data['SMA']


# Example usage
if __name__ == "__main__":
    sma_values = plot_closing_vs_sma(
        ticker="SPY", 
        start="2023-01-01", 
        period=30,
        save_to_csv=True,        # <-- To turn saving on/off here
        csv_filename="spy_sma.csv"
    )

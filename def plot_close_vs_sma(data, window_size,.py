import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


def plot_annotated_runs(data, window_size, years, ticker="SPY"):
    """
    Plots daily closing price and SMA for a given range of years,
    with colored markers for upward/downward runs and streaks.
    """
    data_years = data[data.index.year.isin(years)]
    if data_years.empty:
        print(f"No data available for {ticker} in years {list(years)}.")
        return

    sma = data_years["Close"].rolling(window=window_size).mean()
    close = data_years["Close"].values
    dates = data_years.index

    # Identify runs and streaks
    colors = []
    markers = []
    streak_lengths = []
    current_streak = 1
    current_dir = None
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            color = 'green'
            marker = '^'
            direction = 'up'
        elif close[i] < close[i-1]:
            color = 'red'
            marker = 'v'
            direction = 'down'
        else:
            color = 'gray'
            marker = 'o'
            direction = None
        if direction == current_dir and direction is not None:
            current_streak += 1
        else:
            current_streak = 1
            current_dir = direction
        colors.append(color)
        markers.append(marker)
        streak_lengths.append(current_streak)

    # Plot
    plt.figure(figsize=(12,6))
    plt.plot(dates, close, label="Daily Close", color="blue")
    plt.plot(dates, sma, label=f"{window_size}-Day SMA", color="orange")

    # Annotate runs and streaks
    for i in range(1, len(close)):
        plt.scatter(dates[i], close[i], color=colors[i-1], marker=markers[i-1], s=60)

    plt.title(f"{ticker} Daily Closing Price vs {window_size}-Day SMA ({min(years)}-{max(years)})\nUpward/Downward Runs and Streaks Highlighted")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    ticker = "SPY"
    years = range(2022, 2025) # <--- Change this range for the years you want to plot
    window_size = 5
    data = yf.Ticker(ticker).history(period="max")
    data.index = pd.to_datetime(data.index)
    plot_annotated_runs(data, window_size, years, ticker)


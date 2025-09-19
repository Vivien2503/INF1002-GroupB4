import yfinance as yf
import matplotlib.pyplot as plt

# Download SPY data
stock_symbol = "SPY"
SPY = yf.Ticker(stock_symbol)
data = SPY.history(period="max")

# Filter data by year
year = 2024
data_year = data[data.index.year == year]
close = data_year["Close"].values

# 1. Count daily upward and downward movements
def count_daily_movements(close_prices):
    up_days = sum(1 for i in range(1, len(close_prices)) if close_prices[i] > close_prices[i-1])
    down_days = sum(1 for i in range(1, len(close_prices)) if close_prices[i] < close_prices[i-1])
    return up_days, down_days


# 2. Simple Moving Average (SMA)
def calculate_sma(data, period):
    """
    Calculate Simple Moving Average (SMA) for given data and period.
    :param data: pandas Series of closing prices
    :param period: integer, number of days for SMA
    :return: pandas Series containing SMA values
    """
    return data.rolling(window=period).mean()


def get_user_inputs():
    stock_symbol = input("Enter stock symbol (e.g., SPY): ").upper()
    start_date = input("Enter start date (YYYY-MM-DD): ")
    end_date = input("Enter end date (YYYY-MM-DD): ")
    sma_period = int(input("Enter SMA period (e.g., 5): "))
    return stock_symbol, start_date, end_date, sma_period
# Get user inputs



# 1. Simple Moving Average (SMA)
def calculate_sma(data, period):
    return data.rolling(window=period).mean()

window_size = 5  # Example window size
sma = calculate_sma(data_year["Close"], window_size)
print(f"\n{window_size}-Day SMA for {year} (first 10):\n", sma.head(10))

import yfinance as yf
import matplotlib.pyplot as plt

# Download SPY data
stock_symbol = "SPY"
SPY = yf.Ticker(stock_symbol)
data = SPY.history(period="max")

# Filter data by year
year = 2024
data_year = data[data.index.year == year]
close = data_year["Close"].values

# ... (your other functions remain the same) ...

# Plot 1: Closing Prices with SMA
window_size = 5
sma = calculate_sma(data_year["Close"], window_size)

plt.figure(figsize=(10,5))  # First figure
plt.plot(data_year.index, data_year["Close"], label="Closing Price", color="blue")
plt.plot(data_year.index, sma, label=f"{window_size}-Day SMA", color="orange")
plt.title(f"{stock_symbol} Closing Prices and SMA ({year})")
plt.xlabel("Date")
plt.ylabel("Price")
plt.legend()
plt.tight_layout()
plt.show()  # Show first figure


# Define close_prices as the closing prices for the selected year
close_prices = data_year["Close"].values

# 2. Upward and Downward Runs
def count_daily_movements(close_prices):
    up_days = sum(1 for i in range(1, len(close_prices)) if close_prices[i] > close_prices[i-1])
    down_days = sum(1 for i in range(1, len(close_prices)) if close_prices[i] < close_prices[i-1])
    return up_days, down_days
up_days, down_days = count_daily_movements(close_prices=close)
print(f"\nIn {year}, Up days: {up_days}, Down days: {down_days}")
# Identify runs
up_runs = []
down_runs = []
current_run = 0
current_dir = None
for i in range(1, len(close_prices)):
    if close_prices[i] > close_prices[i-1]:
        if current_dir == "up":
            current_run += 1
        else:
            if current_dir == "down" and current_run > 0:
                down_runs.append(current_run)
            current_dir = "up"
            current_run = 1
    elif close_prices[i] < close_prices[i-1]:
        if current_dir == "down":
            current_run += 1
        else:
            if current_dir == "up" and current_run > 0:
                up_runs.append(current_run)
            current_dir = "down"
            current_run = 1
    else:
        if current_dir == "up" and current_run > 0:
            up_runs.append(current_run)
        elif current_dir == "down" and current_run > 0:
            down_runs.append(current_run)
        current_dir = None
        current_run = 0
# Add last run
if current_dir == "up" and current_run > 0:
    up_runs.append(current_run)
elif current_dir == "down" and current_run > 0:
    down_runs.append(current_run)
print(f"\nUpward runs: {len(up_runs)}, Longest: {max(up_runs) if up_runs else 0}")
print(f"Downward runs: {len(down_runs)}, Longest: {max(down_runs) if down_runs else 0}")


# Plot 2: Run Lengths Bar Chart
plt.figure(figsize=(10,5))  # Second figure
plt.bar(range(len(up_runs)), up_runs, color='green', label='Upward Runs')
plt.bar(range(len(down_runs)), down_runs, color='red', label='Downward Runs', alpha=0.6)
plt.title(f'Upward/Downward Run Lengths ({year})')
plt.xlabel('Run Number')
plt.ylabel('Run Length')
plt.legend()
plt.tight_layout()
plt.show()  # Show second figure

# 3. Daily Returns
daily_returns = data_year["Close"].pct_change()
print(f"\nDaily returns (first 10):\n", daily_returns.head(10))

# 4. Max Profit Calculation (Best Time to Buy and Sell Stock II)
def max_profit(prices):
    profit = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:
            profit += prices[i] - prices[i-1]
    return profit1
profit = max_profit(close)
print(f"\nMax profit (multiple transactions) for {year}: {profit:.2f}")

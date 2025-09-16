import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd

SPY = yf.Ticker("SPY")
data = SPY.history(period="max")
print(data.to_string())

# Filter data by years 2023 and 2024
years = [2023, 2024]
data_years = data[data.index.year.isin(years)]


# Calculate 5-day Simple Moving Average (SMA) for 2023-2024 (pandas built-in)
sma_5 = data_years["Close"].rolling(window=5).mean()
print("\n5-Day SMA for 2023-2024 (pandas built-in):\n", sma_5)

# Calculate 5-day Simple Moving Average (SMA) for 2023-2024 (manual method)
window = 5
close_values = data_years["Close"].values
sma_manual = np.full(len(close_values), np.nan)
for i in range(window-1, len(close_values)):
	sma_manual[i] = np.mean(close_values[i-window+1:i+1])
print("\n5-Day SMA for 2023-2024 (manual):\n", sma_manual)

# Extract closing prices as numpy array for further calculations
close = data_years["Close"].values


# Count consecutive Upward and Downward days
up_runs = []
down_runs = []
current_run = 0
current_dir = None
for i in range(1, len(close)):
	if close[i] > close[i-1]:
		if current_dir == "up":
			current_run += 1
		else:
			if current_dir == "down" and current_run > 0:
				down_runs.append(current_run)
			current_dir = "up"
			current_run = 1
	elif close[i] < close[i-1]:
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
print(f"Upward runs: {len(up_runs)}")
print(f"Downward runs: {len(down_runs)}")
print(f"Total runs: {len(up_runs) + len(down_runs)}")
if up_runs:
	print(f"Longest upward streak: {max(up_runs)} days")
if down_runs:
	print(f"Longest downward streak: {max(down_runs)} days")


# Compute simple daily returns for 2023-2024 (pandas built-in)
daily_returns_builtin = data_years["Close"].pct_change()
print("\nSimple daily returns (pandas built-in):\n", daily_returns_builtin)

# Compute simple daily returns for 2023-2024 (manual method)
Pt = data_years["Close"].values
rt = np.empty(len(Pt))
rt[0] = np.nan  # First day has no previous day
for t in range(1, len(Pt)):
	rt[t] = (Pt[t] - Pt[t-1]) / Pt[t-1]
print("\nSimple daily returns (manual):\n", rt)


# Calculate max profit (Best Time to Buy and Sell Stock II)
def max_profit(prices):
	profit = 0
	for i in range(1, len(prices)):
		if prices[i] > prices[i-1]:
			profit += prices[i] - prices[i-1]
	return profit

profit = max_profit(close)
print(f"\nMax profit (multiple transactions) for {years}: {profit:.2f}")

# Solution for best time to buy and sell stock (prints buy/sell days for each transaction)
def best_time_to_buy_sell(prices):
	n = len(prices)
	i = 0
	transactions = []
	while i < n - 1:
		# Find next local minima (buy)
		while i < n - 1 and prices[i+1] <= prices[i]:
			i += 1
		if i == n - 1:
			break
		buy = i
		i += 1
		# Find next local maxima (sell)
		while i < n and (i == n-1 or prices[i] >= prices[i-1]):
			if i == n-1 or prices[i+1] < prices[i]:
				sell = i
				transactions.append((buy, sell))
				break
			i += 1
	return transactions

transactions = best_time_to_buy_sell(close)
for idx, (buy, sell) in enumerate(transactions, 1):
	print(f"Transaction {idx}: Buy on day {buy}, Sell on day {sell}, Profit: {close[sell] - close[buy]:.2f}")

# Calculate average closing price for the filtered years
average_close = data_years["Close"].mean()
print(f"Average closing price for SPY in {years}: {average_close}")


# Plot daily closing price vs 5-day SMA for 2023 and 2024 separately
for year in years:
	data_year = data[data.index.year == year]
	sma_5_year = data_year["Close"].rolling(window=5).mean()
	plt.figure(figsize=(12,6))
	plt.plot(data_year.index, data_year["Close"], label="Daily Closing Price", color="blue")
	plt.plot(data_year.index, sma_5_year, label="5-Day SMA", color="red", linestyle="--")
	plt.title(f"SPY Daily Closing Price vs 5-Day SMA ({year})")
	plt.xlabel("Date")
	plt.ylabel("Price")
	plt.legend()
	plt.tight_layout()
	plt.show()


# Plot price chart highlighting upward and downward runs for each year separately
for year in years:
	data_year = data[data.index.year == year]
	close_year = data_year["Close"].values
	colors = []
	for i in range(1, len(close_year)):
		if close_year[i] > close_year[i-1]:
			colors.append('green')  # Upward run
		elif close_year[i] < close_year[i-1]:
			colors.append('red')    # Downward run
		else:
			colors.append('gray')   # No change
	plt.figure(figsize=(12,6))
	plt.plot(data_year.index, close_year, color='black', linewidth=1, label='Closing Price')
	for i in range(1, len(close_year)):
		plt.plot(data_year.index[i-1:i+1], close_year[i-1:i+1], color=colors[i-1], linewidth=2)
	plt.title(f'SPY Closing Price with Upward (green) and Downward (red) Runs ({year})')
	plt.xlabel('Date')
	plt.ylabel('Closing Price')
	plt.legend()
	ax = plt.gca()
	ax.xaxis.set_major_locator(mdates.MonthLocator())
	ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
	plt.xticks(rotation=45)
	plt.tight_layout()
	plt.show()

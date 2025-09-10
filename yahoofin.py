import yfinance as yf
import matplotlib.pyplot as plt

SPY = yf.Ticker("SPY")
data = SPY.history(period="2y")
print(data.to_string())
median_close = data["Close"].median()
print(f"Median closing price for SPY over the last 2 years: {median_close}")

# Plot upward and downward trends with different colors
close_prices = data["Close"].values
for i in range(1, len(close_prices)):
	color = 'green' if close_prices[i] > close_prices[i-1] else 'red'
	plt.plot(data.index[i-1:i+1], close_prices[i-1:i+1], color=color)
plt.title("SPY Closing Prices (Last 2 Years) - Upward/Downward Trends")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.show()
import matplotlib.dates as mdates

# Set x-axis to show month and year
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=45)
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SPY = yf.Ticker("SPY")
data = SPY.history(period="max")
print(data.to_string())

# Calculate average closing price
average_close = data["Close"].mean()
print(f"Average closing price for SPY: {average_close}")

# Plot closing prices as a line graph
plt.figure(figsize=(12,6))
plt.plot(data.index, data["Close"], label="Closing Price", color="blue")
plt.axhline(average_close, color="orange", linestyle="--", label=f"Average: {average_close:.2f}")
plt.title("SPY Closing Prices & Average")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.legend()

# Set x-axis to show month and year
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
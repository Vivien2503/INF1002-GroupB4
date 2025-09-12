import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

SPY = yf.Ticker("SPY")
data = SPY.history(period="max")
print(data.to_string())

# Filter data by year (example: 2024)
year = 2024
data_year = data[data.index.year == year]

# Calculate average closing price for the filtered year
average_close = data_year["Close"].mean()
print(f"Average closing price for SPY in {year}: {average_close}")

# Plot closing prices for the filtered year as a line graph
plt.figure(figsize=(12,6))
plt.plot(data_year.index, data_year["Close"], label=f"Closing Price {year}", color="blue")
plt.axhline(average_close, color="orange", linestyle="--", label=f"Average: {average_close:.2f}")
plt.title(f"SPY Closing Prices & Average ({year})")
plt.xlabel("Date")
plt.ylabel("Closing Price")
plt.legend()

# Set x-axis to show month and year
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=45)
plt.tight_layout()
print("gg")
plt.show()
import yfinance as yf
import matplotlib.pyplot as plt

# Download SPY data
SPY = yf.Ticker("SPY")
data = SPY.history(period="max")

# Filter data by year
year = 2024
data_year = data[data.index.year == year]
close = data_year["Close"].values

# 1. Simple Moving Average (SMA)
def compute_sma(series, window):
    return series.rolling(window=window).mean()

window_size = 5  # Example window size
sma = compute_sma(data_year["Close"], window_size)
print(f"\n{window_size}-Day SMA for {year} (first 10):\n", sma.head(10))

# 2. Upward and Downward Runs
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
print(f"\nUpward runs: {len(up_runs)}, Longest: {max(up_runs) if up_runs else 0}")
print(f"Downward runs: {len(down_runs)}, Longest: {max(down_runs) if down_runs else 0}")

# Bar chart of run lengths
plt.figure(figsize=(10,5))
plt.bar(range(len(up_runs)), up_runs, color='green', label='Upward Runs')
plt.bar(range(len(down_runs)), down_runs, color='red', label='Downward Runs', alpha=0.6)
plt.title(f'Upward/Downward Run Lengths ({year})')
plt.xlabel('Run Number')
plt.ylabel('Run Length')
plt.legend()
plt.tight_layout()
plt.show()



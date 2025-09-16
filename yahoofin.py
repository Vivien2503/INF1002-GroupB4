
import yfinance as yf

# Download SPY data
data = yf.download('SPY', start:='2022-01-01', end='2025-01-01')

# Make sure the index is a DatetimeIndex
data.index = data.index.tz_localize(None)

# ...existing code...
year = 2024
data_year = data[data.index.year == year]

# Daily upward and downward movements
up_runs = []
down_runs = []
# Current direction = current_dir
current_dir = None

year = 2024
data_year = data[data.index.year == year]

# Define 'close' as a NumPy array of closing prices
close = data_year['Close'].values
for i in range(1, len(close)):
    if close[i] > close[i-1]:
        if current_dir == "up":
            current_run+= 1
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
import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Download SPY data
SPY = yf.Ticker("SPY")
data = SPY.history(period="max")

# Filter data by year range (corrected)
start_year = 2022
end_year = 2025
data_filtered = data[(data.index.year >= start_year) & (data.index.year <= end_year)]
close = data_filtered["Close"].values

print(f"Analyzing SPY data from {start_year} to {end_year}")
print(f"Total trading days: {len(data_filtered)}")

# 1. Simple Moving Average (SMA)
def compute_sma(series, window):
    return series.rolling(window=window).mean()

window_size = 5
sma = compute_sma(data_filtered["Close"], window_size)
print(f"\n{window_size}-Day SMA (first 10 values):")
print(sma.head(10))

# 2. Enhanced Upward and Downward Streaks Analysis
def calculate_streaks(prices):
    """
    Calculate consecutive upward and downward streaks
    Returns: up_streaks, down_streaks, streak_info
    """
    if len(prices) < 2:
        return [], [], []
    
    up_streaks = []
    down_streaks = []
    streak_info = []  # Store (start_date, end_date, length, direction, start_price, end_price)
    
    current_streak = 0
    current_direction = None
    streak_start_idx = 0
    
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:  # Upward move
            if current_direction == "up":
                current_streak += 1
            else:
                # End previous downward streak if it exists
                if current_direction == "down" and current_streak > 0:
                    down_streaks.append(current_streak)
                    end_date = data_filtered.index[i-1]
                    streak_info.append((
                        data_filtered.index[streak_start_idx],
                        end_date,
                        current_streak,
                        "down",
                        prices[streak_start_idx],
                        prices[i-1]
                    ))
                
                # Start new upward streak
                current_direction = "up"
                current_streak = 1
                streak_start_idx = i-1
                
        elif prices[i] < prices[i-1]:  # Downward move
            if current_direction == "down":
                current_streak += 1
            else:
                # End previous upward streak if it exists
                if current_direction == "up" and current_streak > 0:
                    up_streaks.append(current_streak)
                    end_date = data_filtered.index[i-1]
                    streak_info.append((
                        data_filtered.index[streak_start_idx],
                        end_date,
                        current_streak,
                        "up",
                        prices[streak_start_idx],
                        prices[i-1]
                    ))
                
                # Start new downward streak
                current_direction = "down"
                current_streak = 1
                streak_start_idx = i-1
        
        # If prices are equal, we continue the current streak without incrementing
    
    # Handle the last streak
    if current_direction == "up" and current_streak > 0:
        up_streaks.append(current_streak)
        streak_info.append((
            data_filtered.index[streak_start_idx],
            data_filtered.index[-1],
            current_streak,
            "up",
            prices[streak_start_idx],
            prices[-1]
        ))
    elif current_direction == "down" and current_streak > 0:
        down_streaks.append(current_streak)
        streak_info.append((
            data_filtered.index[streak_start_idx],
            data_filtered.index[-1],
            current_streak,
            "down",
            prices[streak_start_idx],
            prices[-1]
        ))
    
    return up_streaks, down_streaks, streak_info

# Calculate streaks
up_streaks, down_streaks, streak_details = calculate_streaks(close)

# Print streak statistics
print(f"\n=== STREAK ANALYSIS ===")
print(f"Total upward streaks: {len(up_streaks)}")
print(f"Total downward streaks: {len(down_streaks)}")
print(f"Longest upward streak: {max(up_streaks) if up_streaks else 0} consecutive days")
print(f"Longest downward streak: {max(down_streaks) if down_streaks else 0} consecutive days")
print(f"Average upward streak length: {np.mean(up_streaks):.2f} days" if up_streaks else "No upward streaks")
print(f"Average downward streak length: {np.mean(down_streaks):.2f} days" if down_streaks else "No downward streaks")

# Find and display longest streaks
def find_longest_streaks(streak_details, direction, n=3):
    """Find the n longest streaks in a given direction"""
    filtered_streaks = [s for s in streak_details if s[3] == direction]
    sorted_streaks = sorted(filtered_streaks, key=lambda x: x[2], reverse=True)
    return sorted_streaks[:n]

print(f"\n=== TOP 3 LONGEST UPWARD STREAKS ===")
longest_up = find_longest_streaks(streak_details, "up", 3)
for i, (start_date, end_date, length, direction, start_price, end_price) in enumerate(longest_up, 1):
    gain = ((end_price - start_price) / start_price) * 100
    print(f"{i}. {length} days: {start_date.date()} to {end_date.date()}")
    print(f"   Price: ${start_price:.2f} → ${end_price:.2f} (Gain: {gain:.2f}%)")

print(f"\n=== TOP 3 LONGEST DOWNWARD STREAKS ===")
longest_down = find_longest_streaks(streak_details, "down", 3)
for i, (start_date, end_date, length, direction, start_price, end_price) in enumerate(longest_down, 1):
    loss = ((end_price - start_price) / start_price) * 100
    print(f"{i}. {length} days: {start_date.date()} to {end_date.date()}")
    print(f"   Price: ${start_price:.2f} → ${end_price:.2f} (Loss: {loss:.2f}%)")

# Enhanced visualization
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

# 1. Price chart with longest streaks highlighted
ax1.plot(data_filtered.index, data_filtered['Close'], 'b-', alpha=0.7, linewidth=1)
ax1.set_title(f'SPY Price with Longest Streaks Highlighted ({start_year}-{end_year})')
ax1.set_ylabel('Price ($)')

# Highlight longest streaks
if longest_up:
    start_date, end_date, length, _, _, _ = longest_up[0]
    mask = (data_filtered.index >= start_date) & (data_filtered.index <= end_date)
    ax1.plot(data_filtered.index[mask], data_filtered['Close'][mask], 'g-', linewidth=3, 
             label=f'Longest Up Streak ({length} days)')

if longest_down:
    start_date, end_date, length, _, _, _ = longest_down[0]
    mask = (data_filtered.index >= start_date) & (data_filtered.index <= end_date)
    ax1.plot(data_filtered.index[mask], data_filtered['Close'][mask], 'r-', linewidth=3,
             label=f'Longest Down Streak ({length} days)')

ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. Streak length distribution
all_streaks = up_streaks + down_streaks
ax2.hist([up_streaks, down_streaks], bins=range(1, max(all_streaks)+2), 
         color=['green', 'red'], alpha=0.7, label=['Upward', 'Downward'])
ax2.set_title('Distribution of Streak Lengths')
ax2.set_xlabel('Streak Length (days)')
ax2.set_ylabel('Frequency')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. Streak lengths over time
streak_dates = [s[0] for s in streak_details]
streak_lengths = [s[2] for s in streak_details]
streak_colors = ['green' if s[3] == 'up' else 'red' for s in streak_details]

ax3.scatter(streak_dates, streak_lengths, c=streak_colors, alpha=0.7)
ax3.set_title('Streak Lengths Over Time')
ax3.set_xlabel('Date')
ax3.set_ylabel('Streak Length (days)')
ax3.grid(True, alpha=0.3)

# 4. Cumulative streak analysis
cumulative_up_days = np.cumsum([s for s in up_streaks])
cumulative_down_days = np.cumsum([s for s in down_streaks])

ax4.plot(range(1, len(cumulative_up_days)+1), cumulative_up_days, 'g-', 
         label='Cumulative Up Days', linewidth=2)
ax4.plot(range(1, len(cumulative_down_days)+1), cumulative_down_days, 'r-', 
         label='Cumulative Down Days', linewidth=2)
ax4.set_title('Cumulative Streak Days')
ax4.set_xlabel('Streak Number')
ax4.set_ylabel('Cumulative Days')
ax4.legend()
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 3. Daily Returns Analysis
daily_returns = data_filtered["Close"].pct_change().dropna()
print(f"\n=== DAILY RETURNS ANALYSIS ===")
print(f"Average daily return: {daily_returns.mean()*100:.3f}%")
print(f"Daily return volatility: {daily_returns.std()*100:.3f}%")
print(f"Best single day: {daily_returns.max()*100:.2f}%")
print(f"Worst single day: {daily_returns.min()*100:.2f}%")

# 4. Enhanced Max Profit Calculation
def max_profit_detailed(prices, dates):
    """
    Calculate maximum profit with detailed transaction info
    """
    if len(prices) < 2:
        return 0, []
    
    total_profit = 0
    transactions = []
    i = 0
    
    while i < len(prices) - 1:
        # Find local minimum (buy point)
        while i < len(prices) - 1 and prices[i] >= prices[i + 1]:
            i += 1
        
        if i == len(prices) - 1:
            break
            
        buy_price = prices[i]
        buy_date = dates[i]
        
        # Find local maximum (sell point)
        while i < len(prices) - 1 and prices[i] <= prices[i + 1]:
            i += 1
            
        sell_price = prices[i]
        sell_date = dates[i]
        
        profit = sell_price - buy_price
        total_profit += profit
        
        transactions.append({
            'buy_date': buy_date,
            'sell_date': sell_date,
            'buy_price': buy_price,
            'sell_price': sell_price,
            'profit': profit,
            'return_pct': (profit / buy_price) * 100
        })
    
    return total_profit, transactions

profit, transactions = max_profit_detailed(close, data_filtered.index)
print(f"\n=== OPTIMAL TRADING ANALYSIS ===")
print(f"Maximum profit (multiple transactions): ${profit:.2f}")
print(f"Number of optimal transactions: {len(transactions)}")

if transactions:
    print(f"\nTop 5 Most Profitable Transactions:")
    sorted_transactions = sorted(transactions, key=lambda x: x['return_pct'], reverse=True)
    for i, trans in enumerate(sorted_transactions[:5], 1):
        print(f"{i}. Buy: {trans['buy_date'].date()} at ${trans['buy_price']:.2f}")
        print(f"   Sell: {trans['sell_date'].date()} at ${trans['sell_price']:.2f}")
        print(f"   Profit: ${trans['profit']:.2f} ({trans['return_pct']:.2f}%)")
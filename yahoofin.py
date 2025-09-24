import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Download SPY data
SPY = yf.Ticker("SPY")
data = SPY.history(period="max")

# Filter data by year range
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

# --- streak analysis functions ---
def calculate_streaks(prices):
    if len(prices) < 2:
        return [], [], []
    up_streaks, down_streaks, streak_info = [], [], []
    current_streak = 0
    current_direction = None
    streak_start_idx = 0
    for i in range(1, len(prices)):
        if prices[i] > prices[i-1]:  # Up
            if current_direction == "up":
                current_streak += 1
            else:
                if current_direction == "down" and current_streak > 0:
                    down_streaks.append(current_streak)
                    end_date = data_filtered.index[i-1]
                    streak_info.append((
                        data_filtered.index[streak_start_idx],
                        end_date, current_streak, "down",
                        prices[streak_start_idx], prices[i-1]
                    ))
                current_direction = "up"
                current_streak = 1
                streak_start_idx = i-1
        elif prices[i] < prices[i-1]:  # Down
            if current_direction == "down":
                current_streak += 1
            else:
                if current_direction == "up" and current_streak > 0:
                    up_streaks.append(current_streak)
                    end_date = data_filtered.index[i-1]
                    streak_info.append((
                        data_filtered.index[streak_start_idx],
                        end_date, current_streak, "up",
                        prices[streak_start_idx], prices[i-1]
                    ))
                current_direction = "down"
                current_streak = 1
                streak_start_idx = i-1
    # Final streak
    if current_direction == "up" and current_streak > 0:
        up_streaks.append(current_streak)
        streak_info.append((
            data_filtered.index[streak_start_idx],
            data_filtered.index[-1], current_streak, "up",
            prices[streak_start_idx], prices[-1]
        ))
    elif current_direction == "down" and current_streak > 0:
        down_streaks.append(current_streak)
        streak_info.append((
            data_filtered.index[streak_start_idx],
            data_filtered.index[-1], current_streak, "down",
            prices[streak_start_idx], prices[-1]
        ))
    return up_streaks, down_streaks, streak_info

up_streaks, down_streaks, streak_details = calculate_streaks(close)
print(f"\n=== STREAK ANALYSIS ===")
print(f"Total upward streaks: {len(up_streaks)}")
print(f"Total downward streaks: {len(down_streaks)}")
print(f"Longest upward streak: {max(up_streaks) if up_streaks else 0} days")
print(f"Longest downward streak: {max(down_streaks) if down_streaks else 0} days")
print(f"Average upward streak length: {np.mean(up_streaks):.2f} days" if up_streaks else "No upward streaks")
print(f"Average downward streak length: {np.mean(down_streaks):.2f} days" if down_streaks else "No downward streaks")

def find_longest_streaks(streak_details, direction, n=3):
    filtered_streaks = [s for s in streak_details if s[3] == direction]
    return sorted(filtered_streaks, key=lambda x: x[2], reverse=True)[:n]

print(f"\n=== TOP 3 LONGEST UPWARD STREAKS ===")
for i, (start_date, end_date, length, _, start_price, end_price) in enumerate(find_longest_streaks(streak_details, "up", 3), 1):
    gain = ((end_price - start_price) / start_price) * 100
    print(f"{i}. {length} days: {start_date.date()} → {end_date.date()} | Gain: {gain:.2f}%")

print(f"\n=== TOP 3 LONGEST DOWNWARD STREAKS ===")
for i, (start_date, end_date, length, _, start_price, end_price) in enumerate(find_longest_streaks(streak_details, "down", 3), 1):
    loss = ((end_price - start_price) / start_price) * 100
    print(f"{i}. {length} days: {start_date.date()} → {end_date.date()} | Loss: {loss:.2f}%")

# --- interactive recommendation functions ---
def get_recommendation(target_date_str, data, sma_window=20, lookback_days=5, lookahead_days=10):
    try:
        target_date = pd.to_datetime(target_date_str).tz_localize('UTC')
    except:
        return "Invalid date format. Please use 'YYYY-MM-DD' format."
    if target_date not in data.index:
        closest_date = min(data.index, key=lambda x: abs(x - target_date))
        if abs((closest_date - target_date).days) > 7:
            return f"Date {target_date_str} is too far from available data. Closest date is {closest_date.date()}"
        target_date = closest_date
        print(f"Using closest available date: {target_date.date()}")
    try:
        target_idx = data.index.get_loc(target_date)
    except:
        return "Date not found in data range."
    if target_idx < max(sma_window, lookback_days):
        return f"Not enough historical data for analysis. Need at least {max(sma_window, lookback_days)} days before the target date."
    target_price = data['Close'].iloc[target_idx]
    analysis = {
        'date': target_date.date(),
        'price': target_price,
        'signals': [],
        'score': 0,
        'confidence': 0
    }
    sma = data['Close'].rolling(window=sma_window).mean()
    target_sma = sma.iloc[target_idx]
    if target_price > target_sma * 1.02:
        analysis['signals'].append(f"Price (${target_price:.2f}) is {((target_price/target_sma-1)*100):.1f}% above {sma_window}-day SMA (${target_sma:.2f}) - OVERBOUGHT signal")
        analysis['score'] -= 2
    elif target_price < target_sma * 0.98:
        analysis['signals'].append(f"Price (${target_price:.2f}) is {((target_sma/target_price-1)*100):.1f}% below {sma_window}-day SMA (${target_sma:.2f}) - OVERSOLD signal")
        analysis['score'] += 2
    else:
        analysis['signals'].append(f"Price (${target_price:.2f}) is near {sma_window}-day SMA (${target_sma:.2f}) - NEUTRAL")
    lookback_start = target_idx - lookback_days
    recent_prices = data['Close'].iloc[lookback_start:target_idx+1]
    if len(recent_prices) > 1:
        trend_slope = np.polyfit(range(len(recent_prices)), recent_prices.values, 1)[0]
        if trend_slope > 0:
            analysis['signals'].append(f"Recent {lookback_days}-day trend: UPWARD (${trend_slope:.2f}/day)")
            analysis['score'] -= 1
        else:
            analysis['signals'].append(f"Recent {lookback_days}-day trend: DOWNWARD (${trend_slope:.2f}/day)")
            analysis['score'] += 1
    recent_data = data.iloc[max(0, target_idx-30):target_idx+1]
    recent_high = recent_data['High'].max()
    recent_low = recent_data['Low'].min()
    price_position = (target_price - recent_low) / (recent_high - recent_low)
    if price_position > 0.8:
        analysis['signals'].append(f"Price near 30-day high (${recent_high:.2f}) - potential RESISTANCE")
        analysis['score'] -= 1
    elif price_position < 0.2:
        analysis['signals'].append(f"Price near 30-day low (${recent_low:.2f}) - potential SUPPORT")
        analysis['score'] += 1
    else:
        analysis['signals'].append(f"Price in middle of 30-day range (${recent_low:.2f} - ${recent_high:.2f})")
    if 'Volume' in data.columns:
        avg_volume = data['Volume'].rolling(window=20).mean().iloc[target_idx]
        current_volume = data['Volume'].iloc[target_idx]
        if current_volume > avg_volume * 1.5:
            analysis['signals'].append("High volume day - increased conviction in price move")
            analysis['confidence'] += 1
        elif current_volume < avg_volume * 0.5:
            analysis['signals'].append("Low volume day - less conviction in price move")
            analysis['confidence'] -= 1
    future_validation = ""
    if target_idx + lookahead_days < len(data):
        future_prices = data['Close'].iloc[target_idx:target_idx+lookahead_days+1]
        future_return = (future_prices.iloc[-1] - target_price) / target_price * 100
        if future_return > 2:
            future_validation = f"✓ HINDSIGHT: Price rose {future_return:.1f}% in next {lookahead_days} days - was good BUY"
        elif future_return < -2:
            future_validation = f"✗ HINDSIGHT: Price fell {future_return:.1f}% in next {lookahead_days} days - was good SELL"
        else:
            future_validation = f"→ HINDSIGHT: Price moved {future_return:.1f}% in next {lookahead_days} days - was NEUTRAL"
    if analysis['score'] >= 2:
        recommendation = "🟢 BUY SIGNAL - Multiple indicators suggest good buying opportunity"
    elif analysis['score'] <= -2:
        recommendation = "🔴 SELL SIGNAL - Multiple indicators suggest selling or avoiding"
    elif analysis['score'] == 1:
        recommendation = "🟡 WEAK BUY - Some positive indicators"
    elif analysis['score'] == -1:
        recommendation = "🟡 WEAK SELL - Some negative indicators"
    else:
        recommendation = "⚪ NEUTRAL - Mixed or weak signals"
    confidence_level = "High" if abs(analysis['score']) >= 3 else "Medium" if abs(analysis['score']) >= 2 else "Low"
    return {
        'recommendation': recommendation,
        'confidence': confidence_level,
        'score': analysis['score'],
        'signals': analysis['signals'],
        'future_validation': future_validation,
        'price': target_price,
        'date': analysis['date']
    }

def interactive_date_analysis():
    print("\n" + "="*60)
    print("INTERACTIVE BUY/SELL RECOMMENDATION SYSTEM")
    print("="*60)
    print(f"Available data range: {data_filtered.index[0].date()} to {data_filtered.index[-1].date()}")
    print("Enter 'quit' to exit")
    while True:
        user_input = input("\nEnter a date (YYYY-MM-DD): ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("Exiting interactive mode.")
            break
        result = get_recommendation(user_input, data_filtered)
        if isinstance(result, str):
            print(f"\nError: {result}")
            continue
        if not isinstance(result, dict):
            print("\nError: Analysis result is not a dictionary.")
            continue
        if 'date' not in result:
            print("\nError: Analysis result is missing the 'date' key.")
            continue
        print(f"\n📊 ANALYSIS FOR {result['date']}")
        print(f"💰 Price: ${result.get('price', float('nan')):.2f}")
        print(f"📈 {result.get('recommendation', 'N/A')}")
        print(f"🎯 Confidence: {result.get('confidence', 'N/A')} (Score: {result.get('score', 'N/A')})")
        print("\n📋 Analysis Details:")
        for i, signal in enumerate(result.get('signals', []), 1):
            print(f"  {i}. {signal}")
        if result.get('future_validation'):
            print(f"\n{result['future_validation']}")
        print("-" * 50)

# === AUTO-START INTERACTIVE MODE ===
if __name__ == "__main__":
    # Immediately start the interactive prompt when the script runs
    interactive_date_analysis()
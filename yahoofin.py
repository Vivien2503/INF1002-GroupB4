import os, sys, platform, subprocess, webbrowser
import matplotlib
try:
    matplotlib.use("TkAgg")  
except Exception as e:
    print("Could not set GUI backend (TkAgg):", e)
if sys.platform.startswith("linux") and not os.environ.get("DISPLAY"):
    print("Warning: no DISPLAY detected; GUI windows may not open (headless).")

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path

SHOW_PLOTS = True  

def open_file(path: str):
    try:
        if platform.system() == "Windows":
            os.startfile(path)  
        elif platform.system() == "Darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False)
    except Exception:
        webbrowser.open(f"file://{os.path.abspath(path)}")

def get_data(ticker="SPY", start="2023-01-01", end=None):
    return yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)

def filter_years(df: pd.DataFrame, years=(2023, 2024)) -> pd.DataFrame:
    return df[df.index.year.isin(years)].copy()

def calculate_sma(df: pd.DataFrame, window=5) -> pd.Series:
    return df["Close"].rolling(window=window).mean()

def compute_runs(close_values: np.ndarray):
    up_runs, down_runs = [], []
    current_run = 0
    current_dir = None
    start_index = 0

    for i in range(1, len(close_values)):
        if close_values[i] > close_values[i-1]:
            if current_dir == "up":
                current_run += 1
            else:
                if current_dir == "down" and current_run > 0:
                    down_runs.append({"start": start_index, "length": current_run})
                current_dir = "up"
                current_run = 1
                start_index = i - 1
        elif close_values[i] < close_values[i-1]:
            if current_dir == "down":
                current_run += 1
            else:
                if current_dir == "up" and current_run > 0:
                    up_runs.append({"start": start_index, "length": current_run})
                current_dir = "down"
                current_run = 1
                start_index = i - 1
        else:
            if current_dir == "up" and current_run > 0:
                up_runs.append({"start": start_index, "length": current_run})
            elif current_dir == "down" and current_run > 0:
                down_runs.append({"start": start_index, "length": current_run})
            current_dir = None
            current_run = 0

    if current_run > 0:
        if current_dir == "up":
            up_runs.append({"start": start_index, "length": current_run})
        elif current_dir == "down":
            down_runs.append({"start": start_index, "length": current_run})

    return up_runs, down_runs

def summarize_runs(close_vals: np.ndarray):
    up_runs, down_runs = compute_runs(close_vals)
    up_count, down_count = len(up_runs), len(down_runs)
    longest_up = max(up_runs, key=lambda r: r["length"]) if up_runs else None
    longest_down = max(down_runs, key=lambda r: r["length"]) if down_runs else None
    return {
        "up_runs": up_runs, "down_runs": down_runs,
        "up_count": up_count, "down_count": down_count,
        "longest_up": longest_up, "longest_down": longest_down
    }

def daily_returns(df_yr: pd.DataFrame):
    builtin = df_yr["Close"].pct_change()
    Pt = df_yr["Close"].to_numpy()
    manual = np.full_like(Pt, fill_value=np.nan, dtype=float)
    manual[1:] = (Pt[1:] - Pt[:-1]) / Pt[:-1]
    return builtin, manual

def max_profit_multiple(prices: np.ndarray) -> float:
    return float(np.maximum(prices[1:] - prices[:-1], 0).sum())

def best_time_to_buy_sell(prices: np.ndarray):
    n, i = len(prices), 0
    tx = []
    while i < n - 1:
        while i < n - 1 and prices[i+1] <= prices[i]:
            i += 1
        if i == n - 1:
            break
        buy = i
        i += 1
        while i < n and (i == n - 1 or prices[i] >= prices[i-1]):
            if i == n - 1 or prices[i+1] < prices[i]:
                sell = i
                tx.append((buy, sell))
                break
            i += 1
    return tx

def plot_year_with_runs(df_year: pd.DataFrame, outdir=Path("static"), ticker="SPY"):
    from matplotlib import patheffects as pe

    outdir.mkdir(parents=True, exist_ok=True)
    close = df_year["Close"].to_numpy()
    up_runs, down_runs = compute_runs(close)

    colors = []
    for i in range(1, len(close)):
        if close[i] > close[i-1]:
            colors.append("green")
        elif close[i] < close[i-1]:
            colors.append("red")
        else:
            colors.append("gray")

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, close, color="black", linewidth=1, label="Close", alpha=0.9)

    for i in range(1, len(close)):
        ax.plot(df_year.index[i-1:i+1], close[i-1:i+1],
                color=colors[i-1], linewidth=1.5, alpha=0.8)

    def bold_line(x, y, color, label):
        line, = ax.plot(x, y, color=color, linewidth=4.5, alpha=1.0, zorder=5, label=label)
        line.set_path_effects([
            pe.Stroke(linewidth=7.5, foreground="white", alpha=0.9),
            pe.Normal()
        ])
        return line

    if up_runs:
        up_run = max(up_runs, key=lambda r: r["length"])
        s, e = up_run["start"], up_run["start"] + up_run["length"]
        bold_line(df_year.index[s:e+1], close[s:e+1], "green",
                  f"Longest Up ({up_run['length']} days)")
        ax.text(df_year.index[e], close[e],
                f"Longest Up ({up_run['length']}d)",
                color="green", fontsize=10, fontweight="bold",
                ha="left", va="bottom",
                path_effects=[pe.Stroke(linewidth=3, foreground="white"), pe.Normal()])

    if down_runs:
        down_run = max(down_runs, key=lambda r: r["length"])
        s, e = down_run["start"], down_run["start"] + down_run["length"]
        bold_line(df_year.index[s:e+1], close[s:e+1], "red",
                  f"Longest Down ({down_run['length']} days)")
        ax.text(df_year.index[e], close[e],
                f"Longest Down ({down_run['length']}d)",
                color="red", fontsize=10, fontweight="bold",
                ha="left", va="top",
                path_effects=[pe.Stroke(linewidth=3, foreground="white"), pe.Normal()])

    year = df_year.index[0].year
    ax.set_title(f"{ticker} Closing Price with Up/Down Runs ({year})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend(frameon=True)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    out_path = outdir / f"{ticker}_{year}_runs.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS:
        try:
            plt.show()
        except Exception as e:
            print("Could not show() GUI window:", e)
            open_file(str(out_path))
    plt.close(fig)
    return out_path

def plot_sma(df_year: pd.DataFrame, window=5, outdir=Path("static"), ticker="SPY"):
    outdir.mkdir(parents=True, exist_ok=True)
    sma = calculate_sma(df_year, window=window)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_year.index, df_year["Close"], label="Close")
    ax.plot(df_year.index, sma, label=f"{window}-Day SMA", linestyle="--")
    year = df_year.index[0].year
    ax.set_title(f"{ticker} Close vs {window}-Day SMA ({year})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price")
    ax.legend()
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=45)
    plt.tight_layout()

    out_path = outdir / f"{ticker}_{year}_sma.png"
    plt.savefig(out_path, dpi=144)
    if SHOW_PLOTS:
        try:
            plt.show()
        except Exception as e:
            print("Could not show() GUI window:", e)
            open_file(str(out_path))
    plt.close(fig)
    return out_path

def interactive_date_analysis(data_filtered):
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

def main():
    ticker = "SPY"
    years = (2023, 2024)

    data = get_data(ticker=ticker, start="2023-01-01")
    data_years = filter_years(data, years)
    if data_years.empty:
        print(f"No data for {ticker} within {years}.")
        return

    print(f"Pulled {len(data)} rows; filtered to {len(data_years)} rows for years {years}")

    # Daily returns 
    builtin_ret, manual_ret = daily_returns(data_years)
    print("\nDaily returns (pandas head):")
    print(builtin_ret.head(10))
    print("\nDaily returns (manual head):")
    print(manual_ret[:10])

    # Up/Down runs summary 
    close_vals = data_years["Close"].to_numpy()
    runs = summarize_runs(close_vals)
    print(f"\nUpward runs: {runs['up_count']}")
    print(f"Downward runs: {runs['down_count']}")
    if runs["longest_up"]:
        lu = runs["longest_up"]
        print(f"Longest upward streak: {lu['length']} days (start idx {lu['start']})")
    else:
        print("Longest upward streak: N/A")
    if runs["longest_down"]:
        ld = runs["longest_down"]
        print(f"Longest downward streak: {ld['length']} days (start idx {ld['start']})")
    else:
        print("Longest downward streak: N/A")

    # Max profit & explicit transactions
    profit = max_profit_multiple(close_vals)
    print(f"\nMax profit (multiple transactions) for {years}: {profit:.2f}")
    tx = best_time_to_buy_sell(close_vals)
    if tx:
        for i, (b, s) in enumerate(tx, start=1):
            pnl = close_vals[s] - close_vals[b]
            print(f"Transaction {i}: Buy idx {b}, Sell idx {s}, Profit: {pnl:.2f}")
    else:
        print("No profitable transactions found.")

    # Average close
    avg_close = float(data_years["Close"].mean())
    print(f"\nAverage closing price for {ticker} in {years}: {avg_close:.2f}")

    # Per-year charts
    for yr in years:
        df_year = data[data.index.year == yr].copy()
        if df_year.empty:
            print(f"Warning: no data for {yr}")
            continue
        sma_path = plot_sma(df_year, window=5, ticker=ticker)
        runs_path = plot_year_with_runs(df_year, ticker=ticker)
        print(f"Saved: {sma_path}")
        print(f"Saved: {runs_path}")

    # Interactive recommendation system on data_years
    interactive_date_analysis(data_years)

if __name__ == "__main__":
    print("Matplotlib backend:", matplotlib.get_backend())
    main()
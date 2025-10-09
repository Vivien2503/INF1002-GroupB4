"""
Stock Analysis and Trading Signal System

This program gets stock data, does some basic analysis,
and gives a simple buy/sell/neutral signal. It can also
convert prices to other currencies.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import requests

"""
Set the start and end years for pulling stock data.
"""
START_YEAR = 2023
END_YEAR = 2025


def convert_currency(amount: float, from_cur: str, to_cur: str) -> float | None:
    """
    Convert a price from one currency to another using the Frankfurter API.
    """
    if from_cur == to_cur:
        return amount

    url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_cur}&to={to_cur}"
    try:
        r = requests.get(url).json()
        if "rates" in r and to_cur in r["rates"]:
            return r["rates"][to_cur]
        print(f"[Warning] Currency API unexpected response: {r}")
        return None
    except Exception as e:
        print(f"[Error] Currency conversion failed: {e}")
        return None


def calculate_streaks(prices: np.ndarray, df: pd.DataFrame):
    """
    Check how many days in a row the price went up or down.
    """
    if len(prices) < 2:
        return [], [], []

    up, down, details = [], [], []
    current_streak, direction, start_idx = 0, None, 0

    for i in range(1, len(prices)):
        if prices[i] > prices[i - 1]:
            new_dir = "up"
        elif prices[i] < prices[i - 1]:
            new_dir = "down"
        else:
            continue

        if direction != new_dir:
            if direction and current_streak > 0:
                (up if direction == "up" else down).append(current_streak)
                details.append(
                    (df.index[start_idx], df.index[i - 1],
                     current_streak, direction,
                     prices[start_idx], prices[i - 1])
                )
            direction, current_streak, start_idx = new_dir, 1, i - 1
        else:
            current_streak += 1

    if direction and current_streak > 0:
        (up if direction == "up" else down).append(current_streak)
        details.append(
            (df.index[start_idx], df.index[-1],
             current_streak, direction,
             prices[start_idx], prices[-1])
        )

    return up, down, details


def print_streak_summary(up: list, down: list, details: list) -> None:
    """
    Print how many up and down streaks there were and their lengths.
    """
    print("\n STREAK ANALYSIS ")
    print(f"Upward streaks: {len(up)} | Downward streaks: {len(down)}")
    if up:
        print(f"Longest up streak: {max(up)} days | Avg: {np.mean(up):.2f}")
    if down:
        print(f"Longest down streak: {max(down)} days | Avg: {np.mean(down):.2f}")


def get_runs_analysis(ticker="SPY", start_year=2023, end_year=2025):
    """
    Get a summary of up and down runs for a ticker between two years.
    """
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period="max")
        df = df[(df.index.year >= start_year) & (df.index.year <= end_year)]
        if df.empty:
            return None

        up, down, details = calculate_streaks(df["Close"].values, df)
        return {
            "ticker": ticker,
            "start_year": start_year,
            "end_year": end_year,
            "total_trading_days": len(df),
            "upward_streaks": len(up),
            "downward_streaks": len(down),
            "longest_up_streak": max(up) if up else 0,
            "longest_down_streak": max(down) if down else 0,
            "avg_up_streak": round(np.mean(up), 2) if up else 0,
            "avg_down_streak": round(np.mean(down), 2) if down else 0
        }
    except Exception:
        return None


def get_recommendation(target_date_str: str, df: pd.DataFrame, currency: str,
                       sma_window: int = 20, lookback_days: int = 5, lookahead_days: int = 10) -> dict:
    """
    Give a simple buy, sell or neutral signal for a stock on a given date.
    """
    try:
        target_date = pd.to_datetime(target_date_str).tz_localize("UTC")
    except Exception:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    if target_date not in df.index:
        closest = min(df.index, key=lambda x: abs(x - target_date))
        if abs((closest - target_date).days) > 7:
            return {"error": f"Date {target_date_str} not in range. Closest: {closest.date()}"}
        target_date = closest
        print(f"[Info] Using closest available date: {target_date.date()}")

    target_idx = df.index.get_loc(target_date)
    if target_idx < max(sma_window, lookback_days):
        return {"error": "Not enough history for analysis."}

    price = df["Close"].iloc[target_idx]
    signals, score = [], 0

    # SMA deviation 
    sma = df["Close"].rolling(window=sma_window).mean()
    sma_val = sma.iloc[target_idx]
    diff_abs = price - sma_val
    diff_pct = (diff_abs / sma_val) * 100
    if diff_pct > 2:
        signals.append(f"Price is {diff_abs:+.2f} ({diff_pct:.2f}%) above {sma_window}-day SMA ({sma_val:.2f})")
        score -= 2
    elif diff_pct < -2:
        signals.append(f"Price is {diff_abs:+.2f} ({diff_pct:.2f}%) below {sma_window}-day SMA ({sma_val:.2f})")
        score += 2
    else:
        signals.append(f"Price is {diff_abs:+.2f} ({diff_pct:.2f}%) near {sma_window}-day SMA ({sma_val:.2f})")

    #  Trend slope 
    recent = df["Close"].iloc[target_idx - lookback_days:target_idx + 1]
    slope = np.polyfit(range(len(recent)), recent.values, 1)[0]
    if slope > 0:
        signals.append(f"Upward trend ({slope:.2f}/day)")
        score -= 1
    else:
        signals.append(f"Downward trend ({slope:.2f}/day)")
        score += 1

    # Support/Resistance 
    recent_high = df["High"].iloc[target_idx - 30:target_idx + 1].max()
    recent_low = df["Low"].iloc[target_idx - 30:target_idx + 1].min()
    dist_res_abs = recent_high - price
    dist_res_pct = (dist_res_abs / recent_high) * 100
    dist_sup_abs = price - recent_low
    dist_sup_pct = (dist_sup_abs / recent_low) * 100

    pos = (price - recent_low) / (recent_high - recent_low)
    if pos > 0.8:
        signals.append(f"Price is {dist_res_abs:.2f} ({dist_res_pct:.2f}%) below 30-day resistance ({recent_high:.2f})")
        score -= 1
    elif pos < 0.2:
        signals.append(f"Price is {dist_sup_abs:.2f} ({dist_sup_pct:.2f}%) above 30-day support ({recent_low:.2f})")
        score += 1
    else:
        signals.append(f"Price is between support ({recent_low:.2f}) and resistance ({recent_high:.2f})")

    # Final recommendation
    if score >= 2:
        rec = "BUY SIGNAL"
    elif score <= -2:
        rec = "SELL SIGNAL"
    else:
        rec = "NEUTRAL"
    confidence_pct = int(min(abs(score) * 25, 100))

    converted = price if currency == "USD" else convert_currency(price, "USD", currency)

    return {
        "date": target_date.date(),
        "price_native": price,
        "price_converted": converted,
        "recommendation": rec,
        "confidence_pct": f"{confidence_pct}%",
        "signals": signals,
    }

def get_analysis_for_flask(ticker="SPY", start_year=2023, end_year=2025, analysis_date="2024-01-01", target_currency="USD"):
    """
    Get comprehensive analysis for Flask web interface.
    Combines runs analysis and trading recommendation.
    """
    try:
        # Get runs analysis
        runs_data = get_runs_analysis(ticker, start_year, end_year)
        if runs_data is None:
            return None
        
        # Get stock data for recommendation
        tk = yf.Ticker(ticker)
        df = tk.history(period="max")
        df = df[(df.index.year >= start_year) & (df.index.year <= end_year)]
        if df.empty:
            return None
        
        # Get trading recommendation
        recommendation = get_recommendation(analysis_date, df, target_currency)
        if "error" in recommendation:
            return None
        
        # Combine all data for Flask template
        return {
            "ticker": ticker,
            "analysis_date": analysis_date,
            "target_currency": target_currency,
            "runs_analysis": runs_data,
            "recommendation": recommendation,
            "data_period": f"{start_year}-{end_year}"
        }
        
    except Exception as e:
        print(f"[Error] Analysis failed: {e}")
        return None
    
def interactive_mode() -> None:
    """
    Run the program in interactive mode using the terminal.
    """
    print("\nINTERACTIVE STOCK ANALYSIS\n")

    while True:
        ticker = input("\nEnter stock ticker (e.g. SPY): ").strip().upper()
        if ticker.lower() in ["quit", "exit", "q"]:
            break

        # Validate ticker
        try:
            tk = yf.Ticker(ticker)
            df = tk.history(period="max")
            df = df[(df.index.year >= START_YEAR) & (df.index.year <= END_YEAR)]
            if df.empty:
                print(f"[Error] '{ticker}' is not a valid ticker or has no data in the selected period.")
                continue
        except Exception as e:
            print(f"[Error] Failed to fetch data for '{ticker}': {e}")
            continue

        # Show streak analysis
        up, down, details = calculate_streaks(df["Close"].values, df)
        print_streak_summary(up, down, details)

        # Validate date
        date_in = input("Enter date (YYYY-MM-DD): ").strip()
        if date_in.lower() in ["quit", "exit", "q"]:
            break
        try:
            pd.to_datetime(date_in, format="%Y-%m-%d")
        except ValueError:
            print("[Error] Invalid date format. Please use YYYY-MM-DD.")
            continue

        currency = input("Enter target currency (e.g. EUR, SGD, USD): ").strip().upper()
        if currency.lower() in ["quit", "exit", "q"]:
            break

        result = get_recommendation(date_in, df, currency)
        if "error" in result:
            print(f"[Error] {result['error']}")
            continue

        print(f"\n Analysis for {result['date']} — {ticker} ")
        print(f"Native Price: {result['price_native']:.2f} USD")
        if result["price_converted"] is not None:
            print(f"Converted Price: {result['price_converted']:.2f} {currency}")
        else:
            print(f"Converted Price: Not Available ({currency})")
        print(f"Recommendation: {result['recommendation']}")
        print(f"Confidence: {result['confidence_pct']}")
        print("\nIndicators:")
        for i, s in enumerate(result["signals"], 1):
            print(f"  {i}. {s}")


if __name__ == "__main__":
    interactive_mode()
    print("\nThank you for using the Stock Analysis System. Goodbye!\n")

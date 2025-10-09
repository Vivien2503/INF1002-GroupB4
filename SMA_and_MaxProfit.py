"""
Simple Moving Average (SMA) Module
Calculates and retrieves SMA values for stock data on specific dates.
"""

import yfinance as yf
import pandas as pd
import os
from datetime import date

def get_sma_for_date(
    ticker="SPY",
    start="2023-01-01",
    end=None,
    period=30,
    target_date=None,
    snap_to_previous=True, 
    save_to_csv=False,
    csv_filename="sma_values.csv"
):
    """
    Compute SMA and print the SMA value for a specific date.
    """
    if end is None:
        end = date.today().isoformat()

    # Download data
    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if data.empty:
        print("No data found for the given parameters.")
        return None

    # Compute SMA
    data['SMA'] = data['Close'].rolling(window=period, min_periods=1).mean()

    # Find SMA for the target date
    idx = pd.to_datetime(target_date)
    if idx not in data.index:
        if snap_to_previous:
            prev_idx = data.index[data.index <= idx].max()
            if pd.isna(prev_idx):
                print(f"No trading data available on or before {target_date}.")
                return None
            else:
                sma_value = float(data.loc[prev_idx, 'SMA'].iloc[0])
                print(f"\nRequested {target_date} (non-trading). Nearest trading day: {prev_idx.date()}")
                print(f"SMA on {prev_idx.date()} ({period}-day): {sma_value:.2f}")
                return sma_value
        else:
            print(f"No trading data for {target_date}.")
            return None
    else:
        sma_value = float(data.loc[idx, 'SMA'].iloc[0])
        print(f"\nSMA on {target_date} ({period}-day): {sma_value:.2f}")
        return sma_value

    # Optionally save all SMA values
    if save_to_csv:
        data['SMA'].to_csv(csv_filename)
        print(f"SMA values saved to {os.path.abspath(csv_filename)}")


# Example usage
if __name__ == "__main__":
    ticker = input("Enter stock ticker: ")
    sma_days = int(input("Enter SMA period: "))
    user_date = input("Enter the date (YYYY-MM-DD): ")

    get_sma_for_date(
        ticker=ticker,
        start="2023-01-01",
        period=sma_days,
        target_date=user_date
    )

# Max Profit Calculation part ***

"""
Maximum Profit Calculation Module
Implements Best Time to Buy and Sell Stock II algorithm for multiple transactions.
"""

def max_profit_multiple(prices):
    """
    Calculate max profit with multiple buy/sell transactions allowed.
    """
    profit = 0.0
    for i in range(1, len(prices)):
        g = prices[i] - prices[i - 1]
        if g > 0:
            profit += g
    return float(profit)

def extract_trades(prices):
    """
    Return (buy_index, sell_index) pairs for all profitable trades.
    """
    trades, i, n = [], 0, len(prices)
    while i < n - 1:
        while i < n - 1 and prices[i + 1] <= prices[i]: i += 1
        buy = i
        while i < n - 1 and prices[i + 1] >= prices[i]: i += 1
        sell = i
        if sell > buy: trades.append((buy, sell))
        i += 1
    return trades

def get_max_profit_analysis(ticker="SPY", start="2023-01-01", end=None):
    """
    Function to get max profit analysis that can be called from Flask app.
    Returns: dict with max_profit, num_trades, trading_days, actual_start, actual_end, ticker
    """
    if end is None:
        end = date.today().isoformat()
    
    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if data.empty or "Close" not in data.columns:
        return None
    
    closes = data["Close"].squeeze().astype(float).to_list()
    pairs = extract_trades(closes)
    profit = max_profit_multiple(closes)
    
    return {
        "max_profit": round(profit, 2),
        "num_trades": len(pairs),
        "trading_days": len(closes),
        "actual_start": data.index[0].date().isoformat(),
        "actual_end": data.index[-1].date().isoformat(),
        "ticker": ticker
    }

if __name__ == "__main__":
    # Inputs
    ticker = (input("Enter ticker: ") or "SPY").strip().upper()
    start = (input("Enter start date (YYYY-MM-DD): ").strip() or "2023-01-01")
    end_in = input("Enter end date (YYYY-MM-DD): ").strip()
    end = end_in if end_in else None

    # Download
    data = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
    if data.empty or "Close" not in data.columns:
        print(f"No 'Close' data for {ticker} in {start} to {end or 'today'}.")
        raise SystemExit(0)

    closes = data["Close"].squeeze().astype(float).to_list()
    pairs = extract_trades(closes)
    profit = max_profit_multiple(closes)

    # Summary to console
    actual_start = data.index[0].date()
    actual_end = data.index[-1].date()
    print(f"\n{ticker} from {actual_start} to {actual_end}:")
    print(f"- Trading days: {len(closes)}")
    print(f"- Number of trades: {len(pairs)}")
    print(f"- Max Profit: {profit:.2f}")

    # Build trades dataframe
    rows = []
    for b, s in pairs:
        rows.append({
            "buy_date": data.index[b].date(),
            "sell_date": data.index[s].date(),
            "buy_price": round(closes[b], 4),
            "sell_price": round(closes[s], 4),
            "gain": round(closes[s] - closes[b], 4),
        })
    trades_df = pd.DataFrame(rows, columns=["buy_date","sell_date","buy_price","sell_price","gain"])

    # Save Buy and Sell dates to CSV
    save_csv = input("Save trades to CSV? (y/n): ").strip().lower() == "y"
    if save_csv:
        outname = f"{ticker}_{actual_start}_to_{actual_end}_trades.csv"
        trades_df.to_csv(outname, index=False)
        print(f"Saved trades to: {outname}")
    else:
        print("CSV export skipped.")

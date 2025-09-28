import yfinance as yf
import pandas as pd

def max_profit_multiple(prices):
    profit = 0.0
    for i in range(1, len(prices)):
        g = prices[i] - prices[i - 1]
        if g > 0:
            profit += g
    return float(profit)

def extract_trades(prices):
    trades, i, n = [], 0, len(prices)
    while i < n - 1:
        while i < n - 1 and prices[i + 1] <= prices[i]: i += 1
        buy = i
        while i < n - 1 and prices[i + 1] >= prices[i]: i += 1
        sell = i
        if sell > buy: trades.append((buy, sell))
        i += 1
    return trades

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

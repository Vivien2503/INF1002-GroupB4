# Best Time to Buy and Sell Stock II (multiple transactions allowed)

import yfinance as yf

def max_profit_multiple(prices):
    """
    Return the maximum profit when multiple buy/sell transactions are allowed.
    prices: list of daily prices
    """
    profit = 0.0
    for i in range(1, len(prices)):
        gain = prices[i] - prices[i - 1]
        if gain > 0:
            profit += gain
    return profit

def extract_trades(prices):
    """
    Return a list of (buy_index, sell_index) pairs that achieve the same max profit.
    """
    trades = []
    i, n = 0, len(prices)
    while i < n - 1:
        # find local minimum (buy)
        while i < n - 1 and prices[i + 1] <= prices[i]:
            i += 1
        buy = i

        # find local maximum (sell)
        while i < n - 1 and prices[i + 1] >= prices[i]:
            i += 1
        sell = i

        if sell > buy:
            trades.append((buy, sell))
        i += 1
    return trades

if __name__ == "__main__":
    # --- Example with a small list ---
    prices = [7, 1, 5, 3, 6, 4]
    profit = max_profit_multiple(prices)
    trades = extract_trades(prices)
    print("Example prices:", prices)
    print("Max Profit:", profit)
    print("Trades (buy,sell indices):", trades)

    # --- Example with real S&P 500 ETF (SPY) data ---
    data = yf.download("SPY", start="2023-01-01", end=None, progress=False)
    if "Close" not in data.columns or data["Close"].empty:
        print("No 'Close' price data found for SPY in the given range.")
    else:
        closes = data["Close"].squeeze().astype(float).tolist()
        profit_spy = max_profit_multiple(closes)
        trades_spy = extract_trades(closes)
        print("\nSPY from 2023 to now:")
        print("Max Profit:", profit_spy)
        print("Number of trades:", len(trades_spy))
        # Print actual buy/sell dates and prices
        for buy_idx, sell_idx in trades_spy:
            buy_date = data.index[buy_idx].date()
            sell_date = data.index[sell_idx].date()
            buy_price = closes[buy_idx]
            sell_price = closes[sell_idx]
            print(f"Buy on {buy_date} at {buy_price:.2f}, Sell on {sell_date} at {sell_price:.2f}")

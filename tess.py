"""
SPY Stock Price Analysis and Trading Signal Generator
======================================================
A technical analysis tool for analyzing stock price patterns and generating
buy/sell recommendations based on multiple indicators.

Author: [Your Name]
Date: [Current Date]
Version: 2.0 (Refactored)
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Union
from datetime import datetime

# ============================================================================
# CONFIGURATION SECTION
# ============================================================================
# Default analysis parameters - can be modified as needed
CONFIG = {
    'symbol': 'SPY',           # Stock ticker symbol
    'start_year': 2023,        # Analysis start year
    'end_year': 2025,          # Analysis end year
    'sma_window': 20,          # Simple Moving Average window (days)
    'lookback_days': 5,        # Days to look back for trend analysis
    'lookahead_days': 10,      # Days to look ahead for validation
    'volume_threshold': 1.5,   # High volume multiplier threshold
    'overbought_threshold': 1.02,  # Price/SMA ratio for overbought
    'oversold_threshold': 0.98,     # Price/SMA ratio for oversold
}

# ============================================================================
# DATA ACQUISITION SECTION
# ============================================================================
def load_stock_data(symbol: str, start_year: int, end_year: int) -> pd.DataFrame:
    """
    Download and filter stock data for specified date range.
    
    Parameters:
        symbol: Stock ticker symbol
        start_year: Start year for analysis
        end_year: End year for analysis
    
    Returns:
        Filtered DataFrame with stock data
    """
    ticker = yf.Ticker(symbol)
    data = ticker.history(period="max")
    
    # Filter data to specified date range
    data_filtered = data[(data.index.year >= start_year) & 
                         (data.index.year <= end_year)]
    
    print(f"Loaded {symbol} data from {start_year} to {end_year}")
    print(f"Total trading days: {len(data_filtered)}")
    
    return data_filtered

# ============================================================================
# STREAK ANALYSIS SECTION
# ============================================================================
def analyze_price_streaks(data: pd.DataFrame) -> Dict:
    """
    Analyze consecutive up/down price movements (streaks).
    
    Based on concepts from:
    - "Technical Analysis of Stock Trends" by Edwards & Magee
    - Run analysis in statistical process control
    
    Parameters:
        data: DataFrame with stock price data
    
    Returns:
        Dictionary containing streak statistics and details
    """
    prices = data["Close"].values
    if len(prices) < 2:
        return {'up_streaks': [], 'down_streaks': [], 'details': []}
    
    streaks = {'up': [], 'down': []}
    details = []
    current_streak = 0
    direction = None
    start_idx = 0
    
    for i in range(1, len(prices)):
        # Determine direction change
        if prices[i] > prices[i-1]:
            new_direction = 'up'
        elif prices[i] < prices[i-1]:
            new_direction = 'down'
        else:
            continue  # No change, skip
        
        # Check if direction changed
        if direction != new_direction:
            # Save previous streak if exists
            if direction and current_streak > 0:
                streaks[direction].append(current_streak)
                details.append({
                    'start_date': data.index[start_idx],
                    'end_date': data.index[i-1],
                    'length': current_streak,
                    'direction': direction,
                    'start_price': prices[start_idx],
                    'end_price': prices[i-1],
                    'return': ((prices[i-1] - prices[start_idx]) / prices[start_idx]) * 100
                })
            # Start new streak
            direction = new_direction
            current_streak = 1
            start_idx = i-1
        else:
            current_streak += 1
    
    # Save final streak
    if direction and current_streak > 0:
        streaks[direction].append(current_streak)
        details.append({
            'start_date': data.index[start_idx],
            'end_date': data.index[-1],
            'length': current_streak,
            'direction': direction,
            'start_price': prices[start_idx],
            'end_price': prices[-1],
            'return': ((prices[-1] - prices[start_idx]) / prices[start_idx]) * 100
        })
    
    return {
        'up_streaks': streaks['up'],
        'down_streaks': streaks['down'],
        'details': details
    }

def print_streak_summary(streak_data: Dict) -> None:
    """Print formatted summary of streak analysis."""
    up = streak_data['up_streaks']
    down = streak_data['down_streaks']
    
    print("\n=== STREAK ANALYSIS ===")
    print(f"Total upward streaks: {len(up)}")
    print(f"Total downward streaks: {len(down)}")
    
    if up:
        print(f"Longest upward streak: {max(up)} days")
        print(f"Average upward streak: {np.mean(up):.2f} days")
    
    if down:
        print(f"Longest downward streak: {max(down)} days")
        print(f"Average downward streak: {np.mean(down):.2f} days")
    
    # Show top streaks
    for direction in ['up', 'down']:
        print(f"\n=== TOP 3 {direction.upper()} STREAKS ===")
        dir_streaks = sorted([s for s in streak_data['details'] if s['direction'] == direction],
                           key=lambda x: x['length'], reverse=True)[:3]
        
        for i, streak in enumerate(dir_streaks, 1):
            print(f"{i}. {streak['length']} days: "
                  f"{streak['start_date'].date()} → {streak['end_date'].date()} | "
                  f"Return: {streak['return']:.2f}%")

# ============================================================================
# TECHNICAL INDICATORS SECTION
# ============================================================================
class TechnicalIndicators:
    """
    Calculate technical indicators for trading signals.
    
    References:
    - "Technical Analysis from A to Z" by Steven Achelis
    - Simple Moving Average (SMA) strategy
    - Support/Resistance level analysis
    """
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, window: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return data['Close'].rolling(window=window).mean()
    
    @staticmethod
    def calculate_trend(prices: np.ndarray) -> float:
        """Calculate linear trend using least squares regression."""
        if len(prices) < 2:
            return 0.0
        x = np.arange(len(prices))
        slope, _ = np.polyfit(x, prices, 1)
        return slope
    
    @staticmethod
    def calculate_position_in_range(price: float, high: float, low: float) -> float:
        """Calculate price position within a range (0-1)."""
        if high == low:
            return 0.5
        return (price - low) / (high - low)
    
    @staticmethod
    def analyze_volume(current: float, average: float) -> str:
        """Analyze volume relative to average."""
        ratio = current / average if average > 0 else 1
        if ratio > 1.5:
            return "high"
        elif ratio < 0.5:
            return "low"
        return "normal"

# ============================================================================
# TRADING SIGNAL GENERATION SECTION
# ============================================================================
class TradingSignalGenerator:
    """
    Generate buy/sell recommendations based on multiple technical indicators.
    
    Methodology combines:
    - Mean reversion strategy (price vs SMA)
    - Trend following (recent price momentum)
    - Support/Resistance levels
    - Volume confirmation
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.indicators = TechnicalIndicators()
    
    def generate_signal(self, target_date: str, data: pd.DataFrame) -> Dict:
        """
        Generate trading signal for a specific date.
        
        Parameters:
            target_date: Date string in 'YYYY-MM-DD' format
            data: DataFrame with stock data
        
        Returns:
            Dictionary with recommendation and analysis details
        """
        # Parse and validate date
        try:
            target = pd.to_datetime(target_date).tz_localize('UTC')
        except:
            return {'error': "Invalid date format. Use 'YYYY-MM-DD'"}
        
        # Find closest trading day
        if target not in data.index:
            distances = abs(data.index - target)
            closest_idx = distances.argmin()
            if distances[closest_idx].days > 7:
                return {'error': f"Date too far from available data"}
            target = data.index[closest_idx]
        
        target_idx = data.index.get_loc(target)
        
        # Check data sufficiency
        min_history = max(self.config['sma_window'], self.config['lookback_days'])
        if target_idx < min_history:
            return {'error': f"Insufficient history (need {min_history} days)"}
        
        # Initialize analysis
        analysis = {
            'date': target.date(),
            'price': data['Close'].iloc[target_idx],
            'signals': [],
            'score': 0,
            'recommendation': '',
            'confidence': ''
        }
        
        # 1. SMA Analysis (Mean Reversion)
        sma = self.indicators.calculate_sma(data, self.config['sma_window'])
        target_sma = sma.iloc[target_idx]
        price_to_sma = analysis['price'] / target_sma
        
        if price_to_sma > self.config['overbought_threshold']:
            deviation = (price_to_sma - 1) * 100
            analysis['signals'].append(f"Price {deviation:.1f}% above SMA - OVERBOUGHT")
            analysis['score'] -= 2
        elif price_to_sma < self.config['oversold_threshold']:
            deviation = (1 - price_to_sma) * 100
            analysis['signals'].append(f"Price {deviation:.1f}% below SMA - OVERSOLD")
            analysis['score'] += 2
        else:
            analysis['signals'].append("Price near SMA - NEUTRAL")
        
        # 2. Trend Analysis
        lookback_start = target_idx - self.config['lookback_days']
        recent_prices = data['Close'].iloc[lookback_start:target_idx+1].values
        trend = self.indicators.calculate_trend(recent_prices)
        
        if trend > 0:
            analysis['signals'].append(f"Upward trend (${trend:.2f}/day)")
            analysis['score'] -= 1
        else:
            analysis['signals'].append(f"Downward trend (${trend:.2f}/day)")
            analysis['score'] += 1
        
        # 3. Support/Resistance Analysis
        recent_window = data.iloc[max(0, target_idx-30):target_idx+1]
        position = self.indicators.calculate_position_in_range(
            analysis['price'],
            recent_window['High'].max(),
            recent_window['Low'].min()
        )
        
        if position > 0.8:
            analysis['signals'].append("Near resistance level")
            analysis['score'] -= 1
        elif position < 0.2:
            analysis['signals'].append("Near support level")
            analysis['score'] += 1
        
        # 4. Volume Analysis
        if 'Volume' in data.columns:
            avg_volume = data['Volume'].rolling(20).mean().iloc[target_idx]
            current_volume = data['Volume'].iloc[target_idx]
            volume_status = self.indicators.analyze_volume(current_volume, avg_volume)
            
            if volume_status == "high":
                analysis['signals'].append("High volume - strong conviction")
            elif volume_status == "low":
                analysis['signals'].append("Low volume - weak conviction")
        
        # 5. Generate Recommendation
        if analysis['score'] >= 2:
            analysis['recommendation'] = "🟢 BUY SIGNAL"
            analysis['confidence'] = "High" if analysis['score'] >= 3 else "Medium"
        elif analysis['score'] <= -2:
            analysis['recommendation'] = "🔴 SELL SIGNAL"
            analysis['confidence'] = "High" if analysis['score'] <= -3 else "Medium"
        else:
            analysis['recommendation'] = "⚪ NEUTRAL"
            analysis['confidence'] = "Low"
        
        # 6. Backtesting (if future data available)
        if target_idx + self.config['lookahead_days'] < len(data):
            future_price = data['Close'].iloc[target_idx + self.config['lookahead_days']]
            future_return = ((future_price - analysis['price']) / analysis['price']) * 100
            
            if abs(future_return) > 2:
                outcome = "✓ Good call" if (
                    (future_return > 0 and analysis['score'] > 0) or
                    (future_return < 0 and analysis['score'] < 0)
                ) else "✗ Wrong call"
                analysis['validation'] = f"{outcome}: {future_return:+.1f}% in {self.config['lookahead_days']} days"
        
        return analysis

# ============================================================================
# INTERACTIVE INTERFACE SECTION
# ============================================================================
def run_interactive_analysis(data: pd.DataFrame, config: Dict):
    """
    Run interactive date-based analysis interface.
    """
    generator = TradingSignalGenerator(config)
    
    print("\n" + "="*60)
    print("INTERACTIVE TRADING SIGNAL SYSTEM")
    print("="*60)
    print(f"Data range: {data.index[0].date()} to {data.index[-1].date()}")
    print("Commands: 'quit' to exit, 'help' for info")
    print("-"*60)
    
    while True:
        user_input = input("\nEnter date (YYYY-MM-DD): ").strip().lower()
        
        if user_input in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if user_input == 'help':
            print("\nThis system analyzes stock prices and generates trading signals")
            print("based on technical indicators including SMA, trend, and volume.")
            continue
        
        # Generate signal
        result = generator.generate_signal(user_input, data)
        
        if 'error' in result:
            print(f"\n❌ Error: {result['error']}")
            continue
        
        # Display results
        print(f"\n📊 Analysis for {result['date']}")
        print(f"💰 Price: ${result['price']:.2f}")
        print(f"📈 {result['recommendation']} (Confidence: {result['confidence']})")
        print("\n📋 Indicators:")
        for i, signal in enumerate(result['signals'], 1):
            print(f"  {i}. {signal}")
        
        if 'validation' in result:
            print(f"\n🔮 Hindsight: {result['validation']}")
        
        print("-"*50)

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    """Main execution function."""
    # Load data
    data = load_stock_data(
        CONFIG['symbol'],
        CONFIG['start_year'],
        CONFIG['end_year']
    )
    
    # Perform streak analysis
    streak_data = analyze_price_streaks(data)
    print_streak_summary(streak_data)
    
    # Run interactive analysis
    run_interactive_analysis(data, CONFIG)

if __name__ == "__main__":
    main()
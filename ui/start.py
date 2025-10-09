"""
Flask Web Application for Stock Market Trend Analysis Tool

This module provides a web interface for various stock analysis functions:
- Simple Moving Average calculation
- Daily Returns analysis  
- Maximum Profit calculation
- Interactive Stock Analysis with up/down runs

Dependencies:
- Flask: Web framework
- profit_and_sma.py: SMA and profit analysis functions
- SimpleDailyReturn.py: Daily return calculations
- Buy Sell Analysis.py: Streak and trading analysis

Routes:
- /: Main page with navigation buttons
- /sma, /sma2: Simple Moving Average calculator
- /dailyreturncalc, /dailyreturncalc2: Daily Returns calculator
- /maxprofcalc, /maxprofcalc2: Maximum Profit calculator
- /updwnruns, /updwnruns2: Interactive Stock Analysis
"""

from flask import Flask, render_template, request
from datetime import datetime, timedelta
import sys
import os

# Import functions from profit_and_sma.py
try:
    # Add parent directory to Python path to import profit_and_sma.py
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from profit_and_sma import get_sma_for_date, get_max_profit_analysis
    HAS_PROFIT_SMA = True
    print("Successfully imported profit_and_sma.py functions")
except ImportError as e:
    HAS_PROFIT_SMA = False
    print(f"Warning: Could not import profit_and_sma.py - {e}")

# import functions from SimpleDailyReturn.py
try:
    from SimpleDailyReturn import get_daily_return_analysis
    HAS_DAILY_RETURN = True
    print("Successfully imported SimpleDailyReturn.py functions")
except ImportError as e:
    HAS_DAILY_RETURN = False
    print(f"Warning: Could not import SimpleDailyReturn.py - {e}")

# import functions from Buy Sell Analysis.py
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("buy_sell_analysis", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Buy Sell Analysis.py"))
    buy_sell_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(buy_sell_module)
    get_analysis_for_flask = buy_sell_module.get_analysis_for_flask
    HAS_RUNS_ANALYSIS = True
    print("Successfully imported Buy Sell Analysis.py functions")
except Exception as e:
    HAS_RUNS_ANALYSIS = False
    print(f"Warning: Could not import Buy Sell Analysis.py - {e}")
    
app = Flask(__name__)

# Helper function for common date formatting
def get_today():
    """
    Get current date in YYYY-MM-DD format for HTML date inputs
    
    Returns:
        str: Current date formatted as YYYY-MM-DD
    """
    return datetime.now().strftime('%Y-%m-%d')

# Helper function for error responses
def error_response(message):
    """
    Create standardized error response HTML
    
    Args:
        message (str): Error message to display
        
    Returns:
        str: Formatted HTML error message
    """
    return f"<h2>Error: {message}</h2>"

@app.route('/')
def index():
    """
    Main page route displaying navigation buttons for all analysis tools
    
    Returns:
        str: Rendered index.html template with navigation buttons
    """
    return render_template('index.html')

@app.route('/sma')
def sma_page():
    """
    Simple Moving Average input form page
    
    Returns:
        str: Rendered sma.html template with current date
    """
    return render_template('sma.html', max_date=get_today())

@app.route('/updwnruns')
def about_page():
    return render_template('updwnruns.html', max_date=get_today())   

@app.route('/dailyreturncalc')
def contact_page():
    return render_template('dailyreturncalc.html', max_date=get_today())

@app.route('/maxprofcalc')
def services_page():
    return render_template('maxprofcalc.html', max_date=get_today())

@app.route('/sma2', methods=['POST'])
def sma2():
    end_date_raw = request.form['end_date']
    sma_period = request.form.get('sma_period', 30)
    ticker = request.form.get('ticker', 'SPY').upper().strip()
    
    try:
        # Validate ticker input
        if not ticker:
            return error_response("Please enter a ticker symbol.")
        
        # convert the end date from string to date object
        end = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
        sma_period = int(sma_period)
        
        if sma_period < 1:
            return error_response("SMA period must be at least 1 day.")
        
        # Automatically calculate start date with sufficient buffer
        # Use enough days to ensure we have sufficient trading data
        # Rule of thumb: SMA period * 1.5 + 30 days buffer
        buffer_days = max(60, int(sma_period * 1.5) + 30)
        calculated_start = end - timedelta(days=buffer_days)
        start_date_raw = calculated_start.strftime("%Y-%m-%d")
        
        # Format end date for display
        end_date = end.strftime("%d-%m-%Y")
        
        # checks if profit_and_sma.py is available
        if not HAS_PROFIT_SMA:
            return error_response("profit_and_sma.py module is required but not available.")
        
        # use profit_and_sma.py function to get SMA
        sma_result = get_sma_for_date(
            ticker=ticker,
            start=start_date_raw,
            end=end_date_raw,
            period=sma_period,
            target_date=end_date_raw,
            snap_to_previous=True
        )
        
        if sma_result is None:
            return error_response(f"No SMA data available for {ticker} with the selected parameters. Please check if the ticker symbol is valid and data is available for the selected date range.")

        return render_template(
            'sma2.html',
            ticker=ticker,
            end_date=end_date,
            period=sma_period,
            sma_value=round(sma_result, 2)
        )

    except ValueError as e:
        return error_response(f"Invalid input - {str(e)}. Please check your date and SMA period.")
    except Exception as e:
        return error_response(f"{str(e)}. Please try a different date or check if the ticker symbol '{ticker}' is valid.")

@app.route('/maxprofcalc2', methods=['POST'])
def maxprofcalc2():
    start_date_raw = request.form['start_date']
    end_date_raw = request.form['end_date']
    ticker = request.form.get('ticker', 'SPY').strip().upper()
    
    try:
        start = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
        
        if start > end:
            return "<h2>Error: Start date must be before end date.</h2>"
        
        start_date = start.strftime("%d-%m-%Y")
        end_date = end.strftime("%d-%m-%Y")
        
        # checks if profit_and_sma.py is available
        if not HAS_PROFIT_SMA:
            return "<h2>Error: profit_and_sma.py module is required but not available.</h2>"
        
        # uses profit_and_sma.py function to get max profit analysis
        result = get_max_profit_analysis(
            ticker=ticker,
            start=start_date_raw,
            end=end_date_raw
        )
        
        if result is None:
            return f"<h2>No data available for {ticker} in the selected date range.</h2>"

        return render_template(
            'maxprofcalc2.html',
            start_date=start_date,
            end_date=end_date,
            ticker=result['ticker'],
            max_profit=result['max_profit'],
            num_trades=result['num_trades'],
            trading_days=result['trading_days']
        )

    except ValueError as e:
        return f"<h2>Error: Invalid input - {str(e)}. Please check your dates.</h2>"
    except Exception as e:
        return f"<h2>Error: {str(e)}. Please try different parameters.</h2>"

@app.route('/dailyreturncalc2', methods=['POST'])
def dailyreturncalc2():
    target_date_raw = request.form['target_date']
    ticker = request.form.get('ticker', 'SPY').strip().upper()
    
    try:
        target_date = datetime.strptime(target_date_raw, "%Y-%m-%d").date()
        
        date_display = target_date.strftime("%d-%m-%Y")
        
        # checks if SimpleDailyReturn.py is available
        if not HAS_DAILY_RETURN:
            return "<h2>Error: SimpleDailyReturn.py module is required but not available.</h2>"
        
        # uses SimpleDailyReturn.py function to get daily return analysis
        result = get_daily_return_analysis(
            ticker=ticker,
            target_date=target_date_raw
        )
        
        if result is None:
            return f"<h2>No trading data for {ticker} on {date_display} (market closed or holiday).</h2>"

        return render_template(
            'dailyreturncalc2.html',
            date=date_display,
            ticker=result['ticker'],
            close_price=result['close_price'],
            builtin_return=result['builtin_return'],
            manual_return=result['manual_return']
        )

    except ValueError as e:
        return f"<h2>Error: Invalid date format - {str(e)}. Please use YYYY-MM-DD.</h2>"
    except Exception as e:
        return f"<h2>Error: {str(e)}. Please try different parameters.</h2>"

@app.route('/updwnruns2', methods=['POST'])
def updwnruns2():
    ticker = request.form.get('ticker', 'SPY').strip().upper()
    analysis_date = request.form.get('analysis_date', '').strip()
    target_currency = request.form.get('target_currency', 'USD').strip().upper()
    
    try:
        if not analysis_date:
            return "<h2>Error: Analysis date is required.</h2>"
        
        # Automatically calculate start and end years from analysis date
        analysis_year = datetime.strptime(analysis_date, "%Y-%m-%d").year
        start_year = analysis_year - 2  # 3 years of historical data
        end_year = analysis_year
        
        # checks if Buy Sell Analysis.py is available
        if not HAS_RUNS_ANALYSIS:
            return "<h2>Error: Buy Sell Analysis.py module is required but not available.</h2>"
        
        # use Buy Sell Analysis.py function to get comprehensive analysis
        result = get_analysis_for_flask(
            ticker=ticker,
            start_year=start_year,
            end_year=end_year,
            analysis_date=analysis_date,
            target_currency=target_currency
        )
        
        if result is None:
            return f"<h2>No data available for {ticker} for the analysis period.</h2>"

        return render_template(
            'updwnruns2.html',
            result=result
        )

    except ValueError as e:
        return f"<h2>Error: Invalid input - {str(e)}. Please check your parameters.</h2>"
    except Exception as e:
        return f"<h2>Error: {str(e)}. Please try different parameters.</h2>"

if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'development'
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
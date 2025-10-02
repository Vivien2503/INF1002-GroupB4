from flask import Flask, render_template, request
from datetime import datetime
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

@app.route('/')
def index():
    return '''
    <html>
    <head>
    <style>
    body {
    text-align: center;
    }
    
    .button-box {
        border: none;
        color: black;
        padding: 15px 32px;
        text-align: center;
        font-size: 16px;
        margin: 10px;
        cursor: pointer;
        border-radius: 8px;
        display: inline-block;
    }
    
    .red { background-color: #f44336; }
    .blue { background-color: #2196F3; }
    .orange { background-color: #ff9800; }
    .green { background-color: #4CAF50; }

    .button-box:hover { opacity: 0.8; }
    </style>
    </head>
    <body>
        <h1>Hello! Welcome to the Stock Market Analyst For the SPDR S&P 500 ETF (SPY)</h1>
        <p style="font-size: 24px;">Choose one of the following functions:</p>
        
        <div> 
            <form action="/sma" method="GET" style="display: inline;">
                <button type="submit" class="button-box red">Simple Moving Average<br>Calculation</button>
            </form>
            
            <form action="/updwnruns" method="GET" style="display: inline;">
                <button type="submit" class="button-box blue">Interactive Stock<br>Analysis</button>
            </form>
            
            <form action="/dailyreturncalc" method="GET" style="display: inline;">
                <button type="submit" class="button-box orange">Daily Returns<br>Calculation</button>
            </form>
            
            <form action="/maxprofcalc" method="GET" style="display: inline;">
                <button type="submit" class="button-box green">Maximum Profit<br>Calculation</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/sma')
def sma_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('sma.html', max_date=today)

@app.route('/updwnruns')
def about_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('updwnruns.html', max_date=today)   

@app.route('/dailyreturncalc')
def contact_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('dailyreturncalc.html', max_date=today)

@app.route('/maxprofcalc')
def services_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('maxprofcalc.html', max_date=today)

@app.route('/sma2', methods=['POST'])
def sma2():
    start_date_raw = request.form['start_date']
    end_date_raw = request.form['end_date']
    sma_period = request.form.get('sma_period', 30)
    
    try:
        # Convert dates and SMA period
        start = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
        sma_period = int(sma_period)
        
        # Validate inputs
        if sma_period < 1:
            return "<h2>Error: SMA period must be at least 1 day.</h2>"
        if start > end:
            return "<h2>Error: Start date must be before end date.</h2>"
        
        # Format dates for display
        start_date = start.strftime("%d-%m-%Y")
        end_date = end.strftime("%d-%m-%Y")
        
        # Check if profit_and_sma.py is available
        if not HAS_PROFIT_SMA:
            return "<h2>Error: profit_and_sma.py module is required but not available.</h2>"
        
        # Use profit_and_sma.py function to get SMA
        sma_result = get_sma_for_date(
            ticker="SPY",
            start=start_date_raw,
            end=end_date_raw,
            period=sma_period,
            target_date=end_date_raw,
            snap_to_previous=True
        )
        
        if sma_result is None:
            return "<h2>No SMA data available for the selected parameters.</h2>"

        return render_template(
            'sma2.html',
            start_date=start_date,
            end_date=end_date,
            period=sma_period,
            sma_value=round(sma_result, 2)
        )

    except ValueError as e:
        return f"<h2>Error: Invalid input - {str(e)}. Please check your dates and SMA period.</h2>"
    except Exception as e:
        return f"<h2>Error: {str(e)}. Please try different dates.</h2>"

@app.route('/maxprofcalc2', methods=['POST'])
def maxprofcalc2():
    start_date_raw = request.form['start_date']
    end_date_raw = request.form['end_date']
    ticker = request.form.get('ticker', 'SPY').strip().upper()
    
    try:
        # Convert dates
        start = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
        
        # Validate inputs
        if start > end:
            return "<h2>Error: Start date must be before end date.</h2>"
        
        # Format dates for display
        start_date = start.strftime("%d-%m-%Y")
        end_date = end.strftime("%d-%m-%Y")
        
        # Check if profit_and_sma.py is available
        if not HAS_PROFIT_SMA:
            return "<h2>Error: profit_and_sma.py module is required but not available.</h2>"
        
        # Use profit_and_sma.py function to get max profit analysis
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
        # Convert date
        target_date = datetime.strptime(target_date_raw, "%Y-%m-%d").date()
        
        # Format date for display
        date_display = target_date.strftime("%d-%m-%Y")
        
        # Check if SimpleDailyReturn.py is available
        if not HAS_DAILY_RETURN:
            return "<h2>Error: SimpleDailyReturn.py module is required but not available.</h2>"
        
        # Use SimpleDailyReturn.py function to get daily return analysis
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
    start_year = int(request.form.get('start_year', 2023))
    end_year = int(request.form.get('end_year', 2025))
    analysis_date = request.form.get('analysis_date', '').strip()
    target_currency = request.form.get('target_currency', 'USD').strip().upper()
    
    try:
        # Validate inputs
        if start_year > end_year:
            return "<h2>Error: Start year must be before or equal to end year.</h2>"
        
        if not analysis_date:
            return "<h2>Error: Analysis date is required.</h2>"
        
        # Check if Buy Sell Analysis.py is available
        if not HAS_RUNS_ANALYSIS:
            return "<h2>Error: Buy Sell Analysis.py module is required but not available.</h2>"
        
        # Use Buy Sell Analysis.py function to get comprehensive analysis
        result = get_analysis_for_flask(
            ticker=ticker,
            start_year=start_year,
            end_year=end_year,
            analysis_date=analysis_date,
            target_currency=target_currency
        )
        
        if result is None:
            return f"<h2>No data available for {ticker} between {start_year}-{end_year}.</h2>"

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
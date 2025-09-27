from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import io
import base64
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
                <button type="submit" class="button-box blue">Upward/Downward<br>Runs</button>
            </form>
            
            <form action="/dailreturncalc" method="GET" style="display: inline;">
                <button type="submit" class="button-box orange">Daily Returns<br>Calculation</button>
            </form>
            
            <form action="/maxprofcalc" method="GET" style="display: inline;">
                <button type="submit" class="button-box green">Maximum Profit<br>Calculation</button>
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/sma',methods=['GET', 'POST'])
def sma_page():
    today = datetime.now().strftime('%Y-%m-%d')
    return render_template('sma.html', max_date=today)

@app.route('/updwnruns',methods=['GET', 'POST'])
def about_page():
    return render_template('updwnruns.html')   

@app.route('/dailreturncalc',methods=['GET', 'POST'])
def contact_page():
    return render_template('dailyreturncalc.html')

@app.route('/maxprofcalc',methods=['GET', 'POST'])
def services_page():
    return render_template('maxprofcalc.html')

@app.route('/sma2', methods=['POST'])
def sma2():
    start_date_raw = request.form['start_date']
    end_date_raw = request.form['end_date']
    
    try:
        # Convert dates
        start = datetime.strptime(start_date_raw, "%Y-%m-%d").date()
        end = datetime.strptime(end_date_raw, "%Y-%m-%d").date()
        
        # Only check if start is after end
        if start > end:
            return "<h2>Error: Start date must be before end date.</h2>"
        
        # Format dates for display
        start_date = start.strftime("%d-%m-%Y")
        end_date = end.strftime("%d-%m-%Y")
        
        # Download SPY data using the same format that works in the plot script
        print(f"Attempting to download data from {start_date_raw} to {end_date_raw}")
        df = yf.download("SPY", 
                        start=start_date_raw, 
                        end=end_date_raw, 
                        progress=False)
        
        if df.empty:
            print(f"No data found between {start_date_raw} and {end_date_raw}")
            return "<h2>No trading data available for the selected date range.<br>Note: Data is only available for trading days (excluding weekends and holidays).</h2>"
        
        print(f"Downloaded {len(df)} days of data")

        # Calculate period as the number of trading days between start and end date
        trading_days = len(df)
        
        # Calculate SMA using the number of trading days as the period
        period = trading_days
        df['SMA'] = df['Close'].rolling(window=period, min_periods=1).mean()
        
        # Get the latest SMA value and other statistics
        latest_sma = round(df['SMA'].iloc[-1], 2)
        latest_close = round(df['Close'].iloc[-1], 2)
        first_close = round(df['Close'].iloc[0], 2)

        return render_template(
            'sma2.html',
            start_date=start_date,
            end_date=end_date,
            period=trading_days,
            sma_value=latest_sma,
            first_close=first_close,
            latest_close=latest_close
        )
    except Exception as e:
        return f"<h2>Error: {str(e)}. Please try different dates.</h2>"



if __name__ == '__main__':
    import os
    os.environ['FLASK_ENV'] = 'development'
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
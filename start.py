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
    return render_template('sma.html')

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
    end_date_raw   = request.form['end_date']

    start_date = datetime.strptime(start_date_raw, "%Y-%m-%d").strftime("%d-%m-%Y")
    end_date   = datetime.strptime(end_date_raw, "%Y-%m-%d").strftime("%d-%m-%Y")
    
    df = yf.download("SPY", start=start_date_raw, end=end_date_raw) # Download SPY data
    if df.empty:
        return "<h2>No data available for that date range. Try different dates.</h2>"

    plt.figure(figsize=(10,5)) #Plot
    plt.plot(df.index, df['Close'], label='SPY Close Price')
    plt.legend()
    plt.title("SPY with Simple Moving Average")

    img = io.BytesIO()     # Save plot to base64
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template(
    'sma2.html',
    start_date=start_date,
    end_date=end_date,
    plot_url=plot_url
)



if __name__ == '__main__':
    app.run(debug=True)
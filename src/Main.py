from flask import Flask, render_template, request
import pandas as pd
import plotly
import plotly.express as px

app = Flask(__name__)

# Sample data
portfolio = pd.DataFrame({
    'Symbol': ['AAPL', 'TSLA', 'BTC'], 
    'Qty': [10, 5, 2],
    'Price': [100, 200, 30000]
})

equity = pd.DataFrame({
    'Date': pd.date_range('2023-01-01', periods=30),
    'Equity': [100000 + (i*1000) for i in range(30)] 
})

@app.route('/')
def dashboard():
    fig = px.line(equity, x='Date', y='Equity')
    return render_template('dashboard.html', 
        portfolio=portfolio.to_html(),
        equity=plotly.offline.plot(fig, output_type='div')
    )

@app.route('/trade')
def trade():
    return render_template('trade.html') 

# Other view functions and templates 

if __name__ == '__main__':
    app.run(host='0.0.0.0')
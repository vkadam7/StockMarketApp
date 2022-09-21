from statistics import mean
from flask import Flask, session, render_template, request, redirect, url_for
from stockData import StockData, doesThatStockExist
import pyrebase
import plotly
import numpy as np

app = Flask(__name__)

config = {
'apiKey': "AIzaSyCLXmXYf9D0k_frKUquLoXPofRsWfwP3po",
'authDomain': "stockmarketapp-bb30c.firebaseapp.com",
'projectId': "stockmarketapp-bb30c",
'storageBucket': "stockmarketapp-bb30c.appspot.com",
'messagingSenderId': "873475091746",
'appId': "1:873475091746:web:08017b0f8ad6a57cf5497b",
'measurementId': "G-XVH9S3L9JM",
'databaseURL' : 'https://stockmarketapp-bb30c-default-rtdb.firebaseio.com/'
}

firebase = pyrebase.initialize_app(config)
authen = firebase.auth()

app.secret_key = "aksjdkajsbfjadhvbfjabhsdk"

@app.route('/')
def hello(name=None):
    return render_template('home.html')

@app.route('/stockSearch', methods=['POST', 'GET'])
def stockSearch():
    try:
        if request.method == 'POST':
            if doesThatStockExist(firebase.database(), request.form["searchTerm"]):
                return displayStock(request.form["searchTerm"])
    except KeyError:
        return render_template('404Error.html')
    return render_template('404Error.html')

@app.route('/<ticker>')
def displayStock(ticker):
    stockData = StockData(firebase.database(), ticker, 'daily')
    stock = stockData.stockPageFactory()
    stockMatrix = stockData.getData("2021-09-08", "2022-09-19", "daily")
    dates = [date[0] for date in stockMatrix]
    avgs = [mean([open[2], open[3]]) for open in stockMatrix]
    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=avgs)
    
if __name__ == '__main__':
    app.run(port=1111)
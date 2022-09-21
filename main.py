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
    if request.method == 'POST':
        if doesThatStockExist(firebase.database(), request.form["searchTerm"]):
            return displayStock(request.form["searchTerm"])
    return render_template('404Error.html')

@app.route('/<ticker>')
def displayStock(ticker):
    stockData = StockData(firebase.database(), ticker, 'daily')
    return render_template('stockDisplay.html', stock=stockData.stockPageFactory())
    
if __name__ == '__main__':
    app.run(port=1111)
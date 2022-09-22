from statistics import mean
from flask import Flask, session, render_template, request, redirect, url_for
from StockData import StockData, doesThatStockExist
import pyrebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
dbfire = firestore.client() #firestore database
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
db1 = firebase.database()

app.secret_key = "aksjdkajsbfjadhvbfjabhsdk"

#persons = {"logged_in": False,"uName": "", "uEmail": "", "uID": ""} may not need this, will see

@app.route("/login", methods = ["POST","GET"])
def login():
    if('user' in session): #to check if the user is logged in will change to profile page
        return 'Hi, {}'.format(session['user'])
    if request.method == "POST":
        result = request.form
        email = result["email"]
        passw = result["password"]
        try:
            user = authen.sign_in_with_email_and_password(email,passw)
            session['user'] = email
            print("Log in succesful")
            return render_template('home.html') # this will be a placeholder until I get the database up and running 
        except:
            print("Failed to log in")
            return render_template('login.html')
    else:
        print("didn't work at all")
        return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        
        result = request.form
        email = result["email"]
        Password = result["password"]
        try:
            user = authen.create_user_with_email_and_password(email, Password)
            print("Account Created")
            return render_template('login.html')
        except:
            print("Invalid Registration")
            return render_template('register.html')
          
    return render_template('register.html')   

@app.route("/logout")
def logout():
    session.pop('user')
    return render_template('home.html')

@app.route('/')
def hello(name=None):
    return render_template('home.html')
    
## stockSearch
#   Description: Searchs the database for the search term given by the user
#
#   Input: request.form['searchTerm'] - string input given by the user to 
#   search for a stock
#
#   Referenced: doesThatStockExist(db, string) - searchs the database for
#   the given string to see if it matchs an entry ID
#   displayStock(ticker) - renders the webpage for the searched for stock
#   ticker (if found)
#
#   Author: Ian McNulty
@app.route('/stockSearch', methods=['POST', 'GET'])
def stockSearch():
    try:
        if request.method == 'POST':
            if doesThatStockExist(firebase.database(), request.form["searchTerm"]):
                return displayStock(request.form["searchTerm"])
    except KeyError:
        return render_template('404Error.html')
    return render_template('404Error.html')

## displayStock
#   Description: Creates a StockData object for manipulation and then creates
#   webpage from given stock object
#
#   Input: ticker - the stock ticker searched for in stockSearch, if it is 
#   found in the database
#   startDate - starting date of requested dataset
#   endDate - ending date of requested dataset
#   timespan - amount of time each data point represents
#
#   Referenced: StockData - class that allows for manipulation of data
#   obtained from Realtime Database located on Firebase app
#
#   Author: Ian McNulty
@app.route('/<ticker>')
def displayStock(ticker, startDate="2021-09-08", endDate="2022-09-19", timespan="daily"):
    stockData = StockData(firebase.database(), ticker, timespan)
    global stock
    stock = stockData.stockPageFactory()
    stockMatrix = stockData.getData(startDate, endDate, timespan)
    if stockMatrix != -1:
        dates = [date[0] for date in stockMatrix]
        avgs = [mean([open[2], open[3]]) for open in stockMatrix]
        return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=avgs)
    else:
        return displayStock(ticker)

@app.route('/changeView', methods=['POST'])
def changeStockView():
    if request.method == 'POST':
        return displayStock(stock['ticker'],request.form['startDate'],request.form['endDate'],request.form['timespan'])
    return -1
    
if __name__ == '__main__':
    app.run(port=1111)
    app.run(debug=True)


from flask import Flask, session, render_template, request, redirect, url_for
import pyrebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from statistics import mean
from StockData import StockData, doesThatStockExist
import plotly
import numpy as np


cred = credentials.Certificate("serviceAccountKey.json") #firestore
firebase_admin.initialize_app(cred) #firestore
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

"""""
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), Length(max = 10)])
    email = StringField('Email', validators = [LENGTH_REQUIRED(min = 3, max = 20)])
    username = StringField('Username', validators = [InputRequired(), Length(min = 3, max = 10)])
    password =  PasswordField('Password', validators=[InputRequired(), Length(min = 3, max = 10)])


@app.route('/register', methods = ['GET', 'POST'])
def register():
    form = RegistrationForm()
    if(form.validate_on_submit):
        return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    
    return render_template('register.html', form = form)
"""

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


@app.route("/logout")

def logout():
    session.pop('user')
    return render_template('home.html')


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


if __name__ == '__main__':
    app.run(debug=True)


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


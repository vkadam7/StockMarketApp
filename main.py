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


@app.route("/profile")
def profile():
    if('user' in session): #to check if the user is logged in will change to profile page
       return render_template("profile.html", person = session['user'])
    else:
        redirect(url_for("login"))
#persons = {"logged_in": False,"uName": "", "uEmail": "", "uID": ""} may not need this, will see
# Login
#  This function allows the user to log into the app with correct credentials
#  If correct users will be taken to the profile page
#  If incorrect, users will be taken back to login page
#  Author: Miqdad Hafiz
@app.route("/login", methods = ["POST","GET"])
def login():
    if('user' in session): #to check if the user is logged in will change to profile page
        redirect(url_for("profile"))
        #return 'Hi, {}'.format(session['user'])

    if request.method == "POST":
        result = request.form
        email = result["email"]
        passw = result["password"]
        try:
            user = authen.sign_in_with_email_and_password(email,passw)
            session['user'] = email
            print("Log in succesful.")
            return redirect(url_for("profile")) # this will be a placeholder until I get the database and profile page are up and running 
        except:
            print("Failed to log in")
            return redirect(url_for("login"))
    else:
        print("didn't work at all")
        return render_template('login.html')

@app.route('/register', methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        
        result = request.form
        email = result["email"]
        Password = result["password"]
        NameU = result["Unames"]
        UseN = result["username"]

        try:
            user = authen.create_user_with_email_and_password(email, Password)
            dbfire.collection('Users').add({"Email": email, "Name":NameU, "UserID": user['localId'], "userName": UseN}) # still need to figure out how to ad userID and grab data
            print("Account Created")
            return redirect(url_for("login"))

        except:
            print("Invalid Registration")
            return redirect(url_for("register"))
          
    return render_template('register.html')   

## Attempt on email verification function by Muneeb Khan (WIP!)
@app.route('/verification', methods = ["POST" , "GET"])
def verification():
    if request.method == "POST":

        result = request.form
        token = result["token"]
        try:
            user = authen.sign_in_with_custom_token(token)
            return redirect(url_for("login"))

        except:
            print("Invalid token please try again!")
            return redirect(url_for("verification"))

    return render_template("verification.html")


## Password Recovery Function by Muneeb Khan
@app.route('/PasswordRecovery', methods = ["POST", "GET"])
def PasswordRecovery():
    if request.method == "POST":
        
        result = request.form
        email = result["email"]
        try:
            user = authen.send_password_reset_email(email)
            print("Password reset notification was sent to your email")
            return redirect(url_for("login"))
        except:
            print("Email not found")
            return redirect(url_for("PasswordRecovery"))
          
    return render_template("PasswordRecovery.html")   

#Logout
# After user logs out session is ended and user is taken to login page
# Author: Miqdad 
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect(url_for("login"))

#Home
# Landing page of our website
#Author: Miqdad
@app.route('/')
def hello(name=None):
    return render_template('home.html')


@app.route("/home")
def home():
    return render_template('home.html')


## Route for About us and Information pages - Muneeb Khan
@app.route("/aboutus")
def aboutus():
    return render_template('aboutus.html')

@app.route("/information")
def information():
    return render_template('information.html')

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
    stockData = StockData(firebase.database(), ticker)
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
    app.run(debug=True)

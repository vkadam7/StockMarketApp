from asyncio.windows_events import NULL
from re import T
from datetime import datetime
from statistics import mean
from flask import Flask, abort, flash, session, render_template, request, redirect, url_for
import pyrebase
import firebase_admin
from stockSim import StockData, User, Order, Simulation, doesThatStockExist

from firebase_admin import firestore
from firebase_admin import credentials
import pandas as pd
import pyrebase
import firebase_admin

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

#Author: Miqdad Hafiz
@app.route("/profile")
def profile():
    if('user' in session): #to check if the user is logged in will change to profile page
        results = dbfire.collection('Users').where('Email', '==', session['user'])
        for doc in results.stream(): 
            results = doc.to_dict()

        return render_template("profile.html", results = results)
    else:
        redirect(url_for("login"))


# Login
#  This function allows the user to log into the app with correct credentials
#  If correct users will be taken to the profile page
#  If incorrect, users will be taken back to login page
#  Author: Miqdad Hafiz
@app.route("/login", methods = ["POST","GET"])
def login():
    if('user' in session): #to check if the user is logged in will change to profile page
        return redirect(url_for("profile"))

    if request.method == "POST":
        result = request.form
        email = result["email"]
        passw = result["password"]
        try:
            user = authen.sign_in_with_email_and_password(email,passw)
            session['user'] = email
            session['loginFlagPy'] = 1
            ## session['Simulation'] = Simulation.retrieveOngoing(dbfire, email)
            flash("Log in succesful.", "pass")
            return redirect(url_for("profile")) # this will be a placeholder until I get the database and profile page are up and running 
        except:
            flash("Failed to log in", "fail")
            return redirect(url_for("login"))
    else:
        print("Landing on page")
        return render_template('login.html')
    
#Author: Viraj Kadam
@app.route('/register', methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        
        result = request.form
        email = result["email"]
        Password = result["password"]
        confirmPass = result["confirmPassw"]
        NameU = result["Unames"]
        UseN = result["username"]

        doc = dbfire.collection('Users').document(UseN).get()
        if doc.exists:
            grabName = dbfire.collection('Users').where('userName', '==', UseN)
            for docs in grabName.stream(): 
                grabName = docs.to_dict()
            uniqueName = grabName['userName']

        else:
            uniqueName = "usernameoktouse"

        # Variables for Password validation - Muneeb Khan
        digits = any(x.isdigit() for x in Password) # Digits will check for any digits in the password
        specials = any(x == '!' or x == '@' or x == '#' or x == '$' for x in Password) # Specials will check for any specials in the password
        
        # If else conditions to check the password requirements - Muneeb Khan
        if (len(Password) < 6 or len(Password) > 20 or digits == 0 or specials == 0):
            flash("Invalid Password! must contain the following requirements: ")
            flash("6 characters minimum")
            flash("20 characters maximum")
            flash("at least 1 digit")
            flash("at least 1 special character ('!','@','#', or '$'")
        
        elif (Password != confirmPass): # If password and cofirm password don't match
            flash("You're password do not match. Please enter the same password for both fields.")
        
        elif (uniqueName == UseN):
            flash("Username is already taken. Please enter a valid username.") #check to see if username is taken

        else:

            try: 
                user = authen.create_user_with_email_and_password(email, Password)

                #User.registerUser(dbfire, UseN, email, NameU, user['localId'])
                authen.send_email_verification(user['idToken'])
                dbfire.collection('Users').document(UseN).set({"Email": email, "Name":NameU, "UserID": user['localId'], "userName": UseN}) # still need to figure out how to ad userID and grab data
                flash("Account Created, you will now be redirected to verify your account" , "pass")
                dbfire.collection('Users').add({"Email": email, "Name":NameU, "UserID": user['localId'], "userName": UseN}) # still need to figure out how to ad userID and grab data
                flash("Account succesfully created, you may now login" , "pass")

                return redirect(url_for("login"))

            except:
                flash("Invalid Registration" , "fail")
                return redirect(url_for("register"))
          
    return render_template('register.html')   


'''Viraj Kadam. Will include later on
@app.route('/StockDefinitions')
def stockDefinitions():
    return render_template("StockDefinitions.html")'''

## Attempt on email verification function by Muneeb Khan (WIP!)
@app.route('/verification', methods = ["POST" , "GET"])
def verification():
    if request.method == "POST":

        result = request.form
        email = result["email"]
        try:
            user = authen.send_email_verification(email['idToken'])
            print("Verification sent")
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
            user = authen.send_password_reset_email(email) # Will send the notification to the provided email - Muneeb Khan
            flash("Password reset notification was sent to your email", "pass")
            return redirect(url_for("login"))
        except:
            flash("Email not found" , "fail")
            return redirect(url_for("PasswordRecovery"))
          
    return render_template("PasswordRecovery.html")   

#Logout
# After user logs out session is ended and user is taken to login page
# Author: Miqdad 
@app.route("/logout")
def logout():
    session.pop('user')
    session['loginFlagPy'] = 0
    session['Simulation'] = NULL
    flash('logout succesful','pass')
    return redirect(url_for("login"))

#Home
# Landing page of our website
#Author: Miqdad
@app.route('/')
def hello(name=None):
    session['loginFlagPy'] = 0
    return render_template('home.html')


## Route for Home page - Muneeb Khan
@app.route("/home")
def home():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("home.html", person = person)
    else:
        return render_template('home.html')

## Route for About us page - Muneeb Khan
@app.route("/aboutus")
def aboutus():
    if('user' in session): 
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("aboutus.html", person = person)
    else:
        return render_template('aboutus.html')

## Route for Information Page - Muneeb Khan
@app.route("/information")
def information():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("information.html", person = person)
    else:
        return render_template('information.html')

@app.route("/StockDefinitions")
def StockDefinitions():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("StockDefinitions.html", person = person)
    else:
        return render_template('StockDefinitions.html')

## stockSim
#   Description: Brings the logged in user to the stock sim start page, if the user
#   isn't logged in, a 404 page error is given.
#
#   Author: Ian McNulty
@app.route("/stockSimForm", methods=['POST'])
def stockSimForm():
    if 'user' in session:
        return render_template('stockSimForm.html', person=session['user'])
    else:
        return redirect(url_for('fourOhFour'))

## startSimulation
#   Description: 
@app.route("/startSimulation", methods=['POST'])
def startSimulation():
    try:
        if request.method == 'POST':
            session['simulation'] = {
                'simStartDate': request.form['simStartDate'],
                'simEndDate': request.form['simEndDate'],
                'initialCash': request.form['initialCash']
            }
            session['currentCash'] = request.form['initialCash']
            session['portfolioValue'] = request.form['initialCash']
            simulation = Simulation(dbfire, session['user'], request.form['simStartDate'],
                                    request.form['simEndDate'], request.form['initialCash'])
            simulation.createSim()
            return render_template('simulation.html', person=session['user'])
    except KeyError:
        print("KeyError occured: startSimulation")
        return redirect(url_for('fourOhFour'))
        
@app.route("/finishSimulation", methods=['POST', 'GET'])
def finishSimulation():
    sim.finishSimulation()

@app.route("/orderForm/<option>", methods=['POST', 'GET'])
def orderForm(option):
    return -1

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
                return redirect(url_for('displayStock', ticker=request.form["searchTerm"], startDate="2021-09-08", endDate="2022-09-19", timespan="daily"))
            else:
                return redirect(url_for('fourOhFour'))
    except KeyError:
        print("KeyError occured: stockSearch")
        return redirect(url_for('fourOhFour'))
    return redirect(url_for(request.url))

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
def displayStock(ticker):
    startDate = request.args['startDate']
    endDate = request.args['endDate']
    timespan = request.args['timespan']
    stockData = StockData(firebase.database(), ticker)
    global stock
    stock = stockData.stockPageFactory()
    stockMatrix = stockData.getData(startDate, endDate, timespan)
    if stockMatrix != -1:
        if timespan != 'hourly':
            dates = [row[0] for row in stockMatrix]
            avgs = [mean([row[2], row[3]]) for row in stockMatrix]
            return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=avgs)
        else:
            dates = []
            tempDates = [row[0] for row in stockMatrix]
            for row in tempDates:
                for i in range(0, len(tempDates[0])):
                    dates.append(row[i])
            avgs = []
            tempAvgs = [row[1] for row in stockMatrix]
            for row in tempAvgs:
                for i in range(0, len(tempAvgs[0])):
                    avgs.append(row[i])
            return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=avgs)
    else:
        return displayStock(ticker)

## changeStockView
#   Description: Retrieves data from stockView page to determine how to change
#   the view of the stock (monthly instead of weekly, change date range, etc)
#
#   Author: Ian McNulty
@app.route('/changeView', methods=['POST'])
def changeStockView():
    if request.method == 'POST':
        #return displayStock(stock['ticker'],request.form['startDate'],request.form['endDate'],request.form['timespan'])
        
        return redirect(url_for('.displayStock', ticker=stock['ticker'], startDate=request.form['startDate'], endDate=request.form['endDate'], timespan=request.form['timespan']))
    return -1

@app.route("/stockAvailability",methods=['POST'])
def stockAvailability():
    if request.method == 'POST':
        return redirect(url_for('stockDisplay.html',ticker=stock['ticker'],startDate="2021-09-08",endDate="2022-09-19",timespan="daily"))

    return -1    

## 
@app.route('/404Error')
def fourOhFour():
    return render_template('404Error.html')

@app.route('/portfolio')
def Portfolio():
    return render_template('portfolio.html')

## Need to complete this setup route for the dashboard, will show up to the user once they have started the simulation. 
@app.route('/dashboard')
def Dashboard():
    if 'user' in session:
        return render_template('dashboard.html')

@app.route('/')
def method_name():
    pass
    
if __name__ == '__main__':
    app.run(debug=True)

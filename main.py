from asyncio.windows_events import NULL
#from crypt import methods
#from crypt import methods
#from re import T
from datetime import datetime
import math
from operator import itemgetter, mod
import re
from statistics import mean
#from django.shortcuts import render
from flask import Flask, abort, flash, session, render_template, request, redirect, url_for
import pyrebase
import firebase_admin

from stockSim import Quiz, SimulationFactory, StockData, User, Order, Simulation, portfolio
from followers import FollowUnfollow, Recommendation, UserInfo
from firebase_admin import firestore
from firebase_admin import credentials
import numpy as np
import pyrebase
import firebase_admin
from firebase_admin import db

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
db1 = dbfire

app.secret_key = "aksjdkajsbfjadhvbfjabhsdk"

def sessionFlagCheck(loginFlag, simFlag):
    print("loginFlag is: " + str(loginFlag))
    print("simulationFlag is: " + str(simFlag))

#Author: Miqdad Hafiz
#
@app.route("/profile")
def profile():
    if('user' in session): #to check if the user is logged in will change to profile page
        results = dbfire.collection('Users').where('Email', '==', session['user'])
        #Author: Viraj Kadam
        cash = dbfire.collection('Simulations').where('user', '==', session['user']). where('ongoing', '==', 'true') #For simulation status section
        # daysRemaining = (dbfire.collection('Simulations').collection('simName').collection('endDate')) - (dbfire.collection('Simulations').collection('simName').collection('startDate'))
        #Author: Miqdad Hafiz
        for doc in results.stream(): 
            results = doc.to_dict()
        #Author: Viraj Kadam    
        for doc in cash.stream():
            cash = doc.to_dict()
        # for doc in daysRemaining.stream():
        #    daysRemaining = daysRemaining.to_dict()
        return render_template("profile.html", results = results, cash = cash)
    else:
        redirect(url_for("login"))

@app.route("/Leaderboard")
def Leaderboard():
    if('user' in session):
        leaderB = dbfire.collection('Leaderboard').get()
        documentRef = list(doc.to_dict() for doc in leaderB)
        documentRef.sort(key = itemgetter('score'), reverse=True)
        print("about to print leaderboard")
        print(documentRef)
        return render_template("Leaderboard.html",documentRef = documentRef) #placeholder
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
        #try:
        user = authen.sign_in_with_email_and_password(email,passw)
        session['user'] = email
        session['loginFlagPy'] = 1
        if SimulationFactory.existenceCheck(dbfire, email):
            session['simulationFlag'] = 1
        else:
            session['simulationFlag'] = 0
        sessionFlagCheck(session['loginFlagPy'], session['simulationFlag'])
        flash("Log in succesful.", "pass")
        print("Login successful.")
        return redirect(url_for("profile")) # this will be a placeholder until I get the database and profile page are up and running 
        #except:
        #    flash("Failed to log in", "fail")
        #    print("login failed.")
        #    return redirect(url_for("login"))
    else:
        print("Landing on page")
        return render_template('login.html')


#Author: Miqdad Hafiz
@app.route('/social', methods = ["POST", "GET"])
def social():
    if('user' in session):
        if request.method == "POST":
            search = request.form
            searchKey = search["searchUser"]
            doc = dbfire.collection('Users').document(searchKey).get()
            if doc.exists:
                grabUser = dbfire.collection('Users').where('userName', '==', searchKey)
                for docs in grabUser.stream(): 
                    grabUser = docs.to_dict()
                searchResult = grabUser['userName']
                userResult = grabUser
                found = True
            else:
                searchResult = "cantFind"
                found = False
        
            if(found == True ):
                print("HERE COMES THE USERNAME!")
                print(searchResult)
                print(userResult)
                return render_template("userDisplay.html", searchResult = searchResult, userResult = userResult)
            else:
                print("Can't find user.")
                flash("Can't find the user you searched for.")
                return render_template("social.html")
        return render_template("social.html")
            
        

    
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
                authen.send_email_verification(user['idToken'])
                user = authen.create_user_with_email_and_password(email, Password)

                #User.registerUser(dbfire, UseN, email, NameU, user['localId'])
                dbfire.collection('Users').document(UseN).set({"Email": email, "Name":NameU, "UserID": user['localId'], "userName": UseN}) # still need to figure out how to ad userID and grab data
                flash("Account Created, you will now be redirected to verify your account" , "pass")
                flash("Account succesfully created, you may now login" , "pass")

                return redirect(url_for("login"))

            except:
                flash("Invalid Registration" , "fail")
                return redirect(url_for("register"))
          
    return render_template('register.html')   


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
    session['simulationFlag'] = 0
    flash('logout succesful','pass')
    return redirect(url_for("login"))

#Home
# Landing page of our website
#Author: Miqdad
@app.route('/')
def hello(name=None):
    session['loginFlagPy'] = 0
    session['simulationFlag'] = 0
    
    return render_template("home.html")

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
        return render_template("information.html")
    
    
@app.route("/social")
def network():
    if('user' in session):
       
        return render_template("social.html")

@app.route("/StockDefinitions")
def StockDefinitions():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("StockDefinitions.html", person = person)
    else:
        return render_template("StockDefinitions.html")

# Route for Graph pictures page - Muneeb Khan
@app.route("/graphPictures")
def graphPictures():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("graphPictures.html", person = person)
    else:
        return render_template("graphPictures.html")

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
    if ('user' in session):
        try:
            if request.method == 'POST':
                pattern = re.compile("^\d+(.\d{1,2})?$")
                if pattern.match(request.form['initialCash']):
                    if Simulation.checkDates(request.form['simStartDate'], request.form['simEndDate']):
                        session['simulationFlag'] = 1
                        session['simulation'] = {
                            'simStartDate': request.form['simStartDate'],
                            'simEndDate': request.form['simEndDate'],
                            'initialCash': request.form['initialCash']
                        }
                        session['currentCash'] = request.form['initialCash']
                        session['portfolioValue'] = request.form['initialCash']
                        sim = Simulation(dbfire, session['user'], request.form['simStartDate'],
                                                request.form['simEndDate'], request.form['initialCash'])
                        sim.createSim()
                        session['simName'] = sim.simName
                        
                        tickers = []
                        quantities = []
                        profits = []
                        netGainLoss = []
                        sharesPrices = []
                        currentPrices = []
                        volatility = []
                        ##avgPrice = []

                        for entry in Order.stocksBought(dbfire, session['simName']):
                            Portfolio = portfolio(dbfire, entry, session['user'], session['simName'], session['initialCash'])
                            if Portfolio.quantity != 0:
                                tickers.append(entry)
                                quantities.append(Portfolio.quantity)
                                profits.append(Portfolio.profit)
                                sharesPrices.append(Portfolio.avgSharePrice)
                                currentPrices.append(round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(entry), 2))
                                volatility.append(Portfolio.volatility)
                                #netGainLoss.append(Portfolio.percentChange(quantities, session['avgStockPrice'], session['totalPrice'] ))
                        print(tickers)
                        print(quantities)
                        print(profits)
                        print(sharesPrices)
                        print(currentPrices)
                        print(netGainLoss)
                        print(volatility)

                        return render_template('simulation.html', person=session['user'], tickers=tickers, 
                        quantities=quantities, profits=profits, sharesPrices=sharesPrices,
                        currentPrices=currentPrices)      
                    else:
                        flash("Please swap your date values, the starting date must be before the ending date.")
                        return render_template('stockSimForm.html', person=session['user'])
                else:
                    flash("Please enter a valid cash amount.")
                    return render_template('stockSimForm.html', person=session['user'])
        except KeyError:
            print("KeyError occured: startSimulation")
            return redirect(url_for('fourOhFour'))
        except IndexError:
            print("Index Error occured: " + str(IndexError))
            return render_template('stockSimForm.html', person=session['user'])
    else:
        flash("Sorry you must be logged in to view that page.")
        return redirect(url_for("login"))
        
@app.route("/simulation", methods=['POST', 'GET'])
def goToSimulation():
    if ('user' in session):
        try:
            if request.method == 'POST':
                session['simulationFlag'] = 1
                sim = SimulationFactory(dbfire, session['user']).simulation
                session['currentCash'] = round(sim.currentCash,2)
                session['initialCash'] = sim.initialCash
                session['portfolioValue'] = sim.initialCash
                session['simName'] = sim.simName

                tickers = []
                quantities = []
                profits = []
                netGainLoss = []
                sharesPrices = []
                currentPrices = []
                volatility = []
                ##avgPrice = []   
                
                for entry in Order.stocksBought(dbfire, session['simName']):
                    Portfolio = portfolio(dbfire, entry, session['user'], session['simName'], session['initialCash'])
                    if Portfolio.quantity != 0:
                        tickers.append(entry)
                        quantities.append(Portfolio.quantity)
                        profits.append(Portfolio.profit)
                        sharesPrices.append(Portfolio.avgSharePrice)
                        currentPrices.append(round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(entry), 2))
                        volatility.append(Portfolio.volatility)
                        #netGainLoss.append(Portfolio.percentChange(quantities, session['avgStockPrice'], session['totalPrice'] ))
                print(tickers)
                print(quantities)
                print(profits)
                print(sharesPrices)
                print(currentPrices)
                print(netGainLoss)
                print(volatility)

                return render_template('simulation.html', person=session['user'], tickers=tickers, 
                quantities=quantities, profits=profits, sharesPrices=sharesPrices,
                currentPrices=currentPrices, volatility = volatility)
        except KeyError:
            print("KeyError occured: simulation")
            return redirect(url_for('fourOhFour'))
    else:
        flash("Sorry you must be logged in to view that page.")
        return redirect(url_for("login"))
        
@app.route("/finishSimulation", methods=['POST', 'GET'])
def finishSimulation():
    session['simulationFlag'] = 0
    Simulation.finishSimulation(dbfire, session['simName'])
    return redirect(url_for("profile")) 

@app.route("/orderForm", methods=['POST', 'GET'])
def orderFormFill():
    session['option'] = request.form['option']
    session['currentPrice'] = round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(stock['ticker']), 2)
    return render_template('orderForm.html', option=session['option'])

@app.route("/orderCreate", methods=['POST', 'GET'])
def orderCreate():
    if request.form['stockQuantity'].isnumeric():
        session['orderQuantity'] = request.form['stockQuantity']
        session['orderPrice'] = round(int(session['orderQuantity']) * session['currentPrice'], 2)
        return render_template('orderConfirmation.html', option=session['option'])
    else:
        flash("Please enter a valid quantity amount")
        return render_template('orderForm.html', option=session['option'])

@app.route("/orderConfirm", methods=['POST', 'GET'])
def orderConfirm():
    
    order = Order(dbfire, session['simName'], stock, 
                    session['option'], session['orderQuantity'], session['currentPrice'])
    if session['option'] == 'Buy':
        flag = order.buyOrder()
        
    else:
        flag = order.sellOrder()
    if flag == 1:
        flash("Order Complete!")
        session['currentCash'] = round(Simulation.retrieveCurrentCash(dbfire, session['simName']),2)
        tickers = []
        quantities = []
        profits = []
        netGainLoss = []
        sharesPrices = []
        currentPrices = []
        percentage = []
        ##avgPrice = []
        volatility = []
        
        for entry in Order.stocksBought(dbfire, session['simName']):
            Portfolio = portfolio(dbfire, entry, session['user'], session['simName'], session['initialCash'])
            if Portfolio.quantity != 0:
                tickers.append(entry)
                quantities.append(Portfolio.quantity)
                profits.append(Portfolio.profit)
                sharesPrices.append(Portfolio.avgSharePrice)
                currentPrices.append(round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(entry), 2))
                #netGainLoss.append(Portfolio.percentChange(quantities, session['avgStockPrice'], session['totalPrice'] ))
                volatility.append(Portfolio.volatitlity)
        print(tickers)
        print(quantities)
        print(profits)
        print(sharesPrices)
        print(currentPrices)
        print(netGainLoss)
        print(volatility)

        return render_template('simulation.html', person=session['user'], tickers=tickers, 
        quantities=quantities, profits=profits, sharesPrices=sharesPrices,
        currentPrices=currentPrices, volatility = volatility)    
    elif session['option'] == 'Buy' and flag == -1:
        flash("Insufficient funds to complete purchase")
        return render_template('orderForm.html', option=session['option'])
    elif session['option'] == 'Sell' and flag == -1:
        flash("Insufficient shares to complete sale")
        return render_template('orderForm.html', option=session['option'])
    
## stockSearch
#   Description: Searchs the database for the search term given by the user
#
#   Input: request.form['searchTerm'] - string input given by the user to 
#   search for a stock
#
#   Referenced: StockData.stockSearch(db, string) - searchs the database for
#   the given string to see if it matchs an entry ID
#   displayStock(ticker) - renders the webpage for the searched for stock
#   ticker (if found)
#
#   Author: Ian McNulty
@app.route('/stockSearch', methods=['POST', 'GET'])
def stockSearch():
    if ('user' in session):
        try:
            if request.method == 'POST':
                check = StockData.stockSearch(dbfire, request.form["searchTerm"])
                if check[0]:
                    if session['simulationFlag'] == 1:
                        return redirect(url_for('displayStock', ticker=check[1], startDate="2021-09-08", endDate="2022-09-16", timespan="hourly"))
                    else:
                        return redirect(url_for('displayStock', ticker=check[1], startDate="2021-09-08", endDate="2022-09-16", timespan="daily"))
                else:
                    return redirect(url_for('fourOhFour'))
        except KeyError:
            print("KeyError occured: stockSearch")
            return redirect(url_for('fourOhFour'))
        return redirect(url_for(request.url))
    else:
        flash("Sorry you must be logged in to view that page.")
        return redirect(url_for("login"))

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
    session['ticker'] = ticker
    global stock
    if session['simulationFlag'] == 0:
        stockData = StockData(dbfire, ticker)
        stock = stockData.stockJSON()
        #session['stock'] = stock
        stockMatrix = stockData.getData(startDate, endDate, timespan)
        #print(stockMatrix)
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
        #else:
        #    return displayStock(ticker)
    else:
        stockData = SimulationFactory(dbfire, session['user']).simulation.retrieveStock(ticker)
        existenceFlag = True
        for entry in stockData:
            temp = entry.to_dict()
            if temp.get('unavailable') != None:
                existenceFlag = False
        if existenceFlag:
            if timespan == 'hourly' or timespan == 'daily' or timespan == 'weekly' or timespan == 'monthly':
                if timespan == 'hourly':
                    mod = 6
                elif timespan == 'daily':
                    mod = 40
                elif timespan == 'weekly':
                    mod = 40*7
                for entry in stockData:
                    stock = entry.to_dict()
                if stock != -1:
                    dates = []
                    prices = []
                    avgPrice = []
                    for i in range(0, SimulationFactory(dbfire, session['user']).simulation.whatTimeIsItRightNow()):
                        avgPrice.append(stock['prices'][i])
                        if timespan == 'monthly':
                            mod = 40*7*int(stock['dates'][i][5:7])
                        #if timespan == 'hourly' and int(stock['dates'][i][11:13]) == 9:
                        #    mod = 3
                        print(mod)
                        if i % mod == 1:
                            prices.append(mean(avgPrice))
                            if timespan != 'hourly':
                                dates.append(stock['dates'][i][0:10])
                            else:
                                dates.append(stock['dates'][i-1])
                            avgPrice = []
                        #    if int(stock['dates'][i][11:13]) == 9:
                        #        mod = 6
                    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=prices)
            elif timespan == '1minute' or timespan == '5minute':
                for entry in stockData:
                    stock = entry.to_dict()
                    #session['stock'] = stock
                if stock != -1:
                    dates = []
                    prices = []
                    for i in range(1, SimulationFactory(dbfire, session['user']).simulation.whatTimeIsItRightNow()):
                        if timespan == '5minute':
                            tempInterp = np.interp(range(0,3),[0, 2],[stock['prices'][i-1], stock['prices'][i]])
                            for element in tempInterp:
                                element += (np.random.randn() + np.std([stock['prices'][i-1], stock['prices'][i]]))/100
                                prices.append(element)
                            # 15 = index of minute
                            tempDate = list(stock['dates'][i])
                            for j in range(1,3):
                                tempDate[15] = str((j*5)%10)
                                dates.append("".join(tempDate))
                        elif timespan == '1minute':
                            tempInterp = np.interp(range(0,11),[0, 10],[stock['prices'][i-1], stock['prices'][i]])
                            for element in tempInterp:
                                element += (np.random.randn() + np.std([stock['prices'][i-1], stock['prices'][i]]))/50
                                prices.append(element)
                            tempDate = list(stock['dates'][i])
                            for j in range(0,10):
                                tempDate[15] = str(j)
                                dates.append("".join(tempDate))
                    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=prices)
            else:
                for entry in stockData:
                    stock = entry.to_dict()
                    #session['stock'] = stock
                if stock != -1:
                    dates = []
                    prices = []
                    for i in range(0, SimulationFactory(dbfire, session['user']).simulation.whatTimeIsItRightNow()):
                        dates.append(stock['dates'][i])
                        prices.append(stock['prices'][i])
                    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=prices)
        else:
            return redirect(url_for('fourOhFour'))
    return redirect(url_for('fourOhFour'))

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

#Route for the User list - Muneeb Khan
@app.route("/Userlist")
def userlists():
    if ('user' in session):
       # try:
            newuserlist = User.userList(dbfire)

            return render_template('Userlist.html',newuserlist = newuserlist)
       # except:
        #    return redirect(url_for('fourOhFour'))

#Route for the Order list - Muneeb Khan
@app.route("/orderList")
def orderlists():
    if ('user' in session):
        orderlist = Order.orderList(dbfire, session['simName']) # This will have the username show on webpage when logged in - Muneeb Khan

        return render_template('orderList.html',person=session['user'],buys=orderlist['buyOrSell'].to_list(),
        tickers=orderlist['ticker'].to_list(), quantities=orderlist['quantity'].to_list(), prices=orderlist['totalPrice'].to_list())

## 
@app.route('/404Error')
def fourOhFour():
    return render_template('404Error.html',person = session['user'])
    
#@app.route('/startSimulation')
#def portfolioGraph():
#    if 'user' in session:
        

@app.route('/quiz')
def quizpage():
    if ('user' in session):
        quiz = Quiz.retrieveNextQuestion(dbfire, session['user'])

        return render_template('quiz.html', quiz = quiz, questions = quiz['question'], a = quiz['a'], b = quiz['b'],
        c = quiz['c'])
    else:
        return render_template('404Error.html')

#Author: Viraj Kadam   
#Updates user profile  
#class User(Flaskform):
    #picture =  
#    description = StringField('Description')
#    experience = StringField('Experience')
#    submit = SubmitField("Submit")   
    
#@app.route('/update/<int:id>', methods = ['GET', 'POST'])
#def update():
#   updateinfo = User.query.get(id)
#   if request.method == 'POST':
#        update.description = request.form('Description')
#        update.experience = request.form('Experience')
#        try:
#            db.session.commit()
#            flash("User profile updates")
#            return render_template('profile.html')
#        except:
#            flash("Error, unable to update your profile")

#@app.route('/')
#def method_name():
#    pass



    
if __name__ == '__main__':
    app.run(debug=True)
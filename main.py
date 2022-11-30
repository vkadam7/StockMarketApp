from asyncio.windows_events import NULL
#from crypt import methods
#from crypt import methods
#from re import T
from datetime import datetime,date
import math
from operator import itemgetter, mod
import re
from statistics import mean
from datetime import timedelta
import datetime
#from django.shortcuts import render
from flask import Flask, abort, flash, session, render_template, request, redirect, url_for
import pyrebase
import firebase_admin

from stockSim import Quiz, SimulationFactory, StockData, User, Order, Simulation, portfolio, DAYS_IN_MONTH
from followers import FollowUnfollow, UserInfo
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
@app.route("/profile")
def profile():
    if('user' in session): #to check if the user is logged in will change to profile page
        results = dbfire.collection('Users').where('Email', '==', session['user'])
        #Author: Viraj Kadam
        cash = dbfire.collection('Simulations').where('user', '==', session['user']).where('ongoing', '==', True) #For simulation status section
        #daysRemaining = (dbfire.collection('Simulations').collection('simName').collection('endDate')) - (dbfire.collection('Simulations').collection('simName').collection('startDate'))
        #Author: Miqdad Hafiz
        
        leaderboard = dbfire.collection('Leaderboard').where('email', '==', session['user'])
        for doc in results.stream(): 
            results = doc.to_dict()
        #Author: Viraj Kadam    
        for doc in cash.stream():
            cash = doc.to_dict()
        for doc in leaderboard.stream():
            leaderboard = doc.to_dict()
        #endDateFetch = dbfire.collection('Simulations').where('user', '==', session['user']).where('ongoing', '==', True).document('endDate')
        #startDateFetch = dbfire.collection('Simulations').where('user', '==', session['user']).where('ongoing', '==', True).document('startDate')
        #while(startDateFetch >= endDateFetch):
        #    startDate = startDateFetch[0]
        #    endDate = endDateFetch[0]
            

        followingArray = []
        userF = dbfire.collection('Users').where('Email', '==', session['user'])
        for docs in userF.stream():
            userF = docs.to_dict()
            followingArray.extend(userF['FollowingNames'])
        #print("Printing miqdads following list ")
        #print(followingArray)


        #print("Here comes the leaderboard hopefully")
        personalLB1 = []
        for x in followingArray:
            personalLB = dbfire.collection('Leaderboard').where('username', '==', x).get()
            for docus in personalLB:
                personalLB = docus.to_dict()
                personalLB1.append(personalLB)
                
        #print("Here comes personal B")
        #print(personalLB1)    
            
        return render_template("profile.html", results = results, cash = cash, leaderboard = leaderboard, stockNames = session['stockNames'],personalLB1 = personalLB1)

    else:

        redirect(url_for("login"))

#Author: Miqdad Hafiz
@app.route("/Blog", methods = ["POST","GET"])
def Blog():
    if('user' in session):
        followingArray = []
        userF = dbfire.collection('Users').where('Email', '==', session['user'])
        for docs in userF.stream():
            userF = docs.to_dict()
            followingArray.extend(userF['FollowingNames'])
        print("Printing user's following list ")
        print(followingArray)

        print("Here comes the BLOG.")
        blog = []
        for x in followingArray:
            showBlog = dbfire.collection('Blog').where('Author', '==', x).get()
            for docus in showBlog:
                showBlog = docus.to_dict()
                #post.append(showBlog['Post'])
                showBlog['DatePosted'] = str(datetime.datetime.fromtimestamp(showBlog['DatePosted'].timestamp()).strftime("%Y-%m-%d"))
                blog.append(showBlog)
        
        print("Here comes personal B")
        blog.sort(key = itemgetter('DatePosted'), reverse=True)
        print(blog)   
        return render_template("Blog.html", blog = blog)

#Author: Miqdad Hafiz
@app.route("/userPosts", methods = ["POST","GET"])
def userPosts():
    if('user' in session):
        user = dbfire.collection('Users').where('Email', '==', session['user'])
        for doc in user.stream():
            user = doc.to_dict()
        author = user['userName']

        posts = []
        userPost = dbfire.collection('Blog').stream()
        for docs in userPost:
            userPost = docs.to_dict()
            if(userPost['Author'] == author):
                userPost['DatePosted'] = str(datetime.datetime.fromtimestamp(userPost['DatePosted'].timestamp()).strftime("%Y-%m-%d"))
                userPost['DocID'] = docs.id
                posts.append(userPost)
        posts.sort(key = itemgetter('DatePosted'), reverse=True)
        print(posts)
        return render_template("userPosts.html",posts = posts)


#Author: Miqdad Hafiz
@app.route("/postDelete/<id>", methods = ["GET"])
def postDelete(id):
    if('user' in session):
        print("Testing delete")
        print(id)
        dbfire.collection('Blog').document(id).delete()
        flash("Your post has been deleted.")
        return redirect(url_for("userPosts"))

#Author: Miqdad Hafiz
@app.route("/editPost/<id>",methods = ["POST","GET"])
def editPost(id):
    edit = dbfire.collection('Blog').document(id).get()
    edit = edit.to_dict()
    edit['DocID'] = id
    return render_template("editingPost.html", edit = edit)


@app.route("/editingPost/<id>", methods = ["POST","GET"])
def editingPost(id):
    if('user' in session):
        if(request.method == "POST"):
            result = request.form
            editedPost = result["editingthePost"]
            
            
            dbfire.collection('Blog').document(id).update({'Post': editedPost})
            flash("Post has been updated.")
        return redirect(url_for('userPosts'))
#Author: Miqdad Hafiz
@app.route("/postBlog", methods = ["POST","GET"])
def postBlog():
    if('user' in session):
        if(request.method == "POST"):
            result = request.form
            post = result["blogPost"]
            results = dbfire.collection('Users').where('Email', '==', session['user'])
            for docs in results.stream():
                results = docs.to_dict()
            Author = results['userName']
           
            dbfire.collection('Blog').add({"Author": Author,"DatePosted":firestore.SERVER_TIMESTAMP,"Post":post,"Likes":0})
            flash("Your submission has been posted.")
    return render_template("postBlog.html")


#Author: Miqdad Hafiz
@app.route("/Leaderboard")
def Leaderboard():
    if('user' in session):
        leaderB = dbfire.collection('Leaderboard').get()
        documentRef = list(doc.to_dict() for doc in leaderB)
        documentRef.sort(key = itemgetter('score'), reverse=True)
        print("about to print leaderboard")
        print(documentRef)
        return render_template("Leaderboard.html",documentRef = documentRef, stockNames = session['stockNames']) #placeholder
    else:
        redirect(url_for("login"))


# Follow list function updated by Viraj and Muneeb
@app.route("/followers")
def followList():
    if ('user' in session):
        followersList = []
        for entry in dbfire.collection('Users').where('Email','==',session['user']).stream():
            temp = entry.to_dict()
            followersList.extend(temp['FollowerNames'])
        splitNames = [item.split(',') for item in followersList]
        print(splitNames)
        return render_template('followers.html',splitNames = splitNames, stockNames = session['stockNames'])
    else:
        redirect(url_for("login"))

@app.route("/followingList")
def followingList():
    if 'user' in session:
        #followingList = []
        #for entry in dbfire.collection('Users').where('Name', '==', session['user']).stream():
        #    following = entry.to_dict()
        #    followingList.extend(following['FollowingNames'])
            
        #followingListNames = []
        
        #return render_template('followingList.html', followingList = followingList)
        
        followingList= []
        
        for name in dbfire.collection('Users').where('Name', '==', session['user']).stream():
            temp = name.to_dict()
            followingList.extend(name['FollowingNames'])
        names = [item.split(',') for item in followingList]
        print(names)
        return render_template('followingList.html', names = names, stockNames = session['stockNames'])
    
#Route for the Order list - Muneeb Khan
#@app.route("/orderList")
#def orderlists():
#    if ('user' in session):
#        orderlist = Order.orderList(dbfire, session['simName']) # This will have the username show on webpage when logged in - Muneeb Khan

#        return render_template('orderList.html',person=session['user'],buys=orderlist['buyOrSell'].to_list(), dates=orderlist['dayOfPurchase'].to_list(),
#        tickers=orderlist['ticker'].to_list(), quantities=orderlist['quantity'].to_list(), prices=orderlist['totalPrice'].to_list())

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
        check, session['simName'] = SimulationFactory.existenceCheck(dbfire, email)
        if check:
            session['simulationFlag'] = 1
            sharesValue, currentCash = Simulation.getPortfolioValue(dbfire, session['simName'])
            session['portfolioValue'] = "%.2f" % round(sharesValue, 2)
            session['currentCash'] = "%.2f" % round(currentCash, 2)
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
        return render_template('login.html', stockNames = session['stockNames'])


#Author: Miqdad Hafiz
@app.route('/social', methods = ["POST", "GET"])
def social():
    if('user' in session):
        if request.method == "POST":
            search = request.form
            searchKey = search["searchUser"]
            
            grabUser = dbfire.collection('Users').where('userName', '==', searchKey).get()
            found = True
            size = len(grabUser)
            print(size, "try block 1")
            if(size == 0):
                grabUser = dbfire.collection('Users').where('Name', '==', searchKey).get()
                found = True
                size = len(grabUser)
                print(size, "try block 2")
                if(size == 0):
                    found = False

            
                
            if(found == True ):
                for docs in grabUser: 
                    grabUser = docs.to_dict()
                userResult = grabUser
                session['userResults'] = userResult

                #check to see if user searched themselves
                userEmail = session['user']
                matching = False
                alreadyFollows = False
                if(userEmail == userResult['Email']):
                    matching = True
                else:
                    matching = False
                
                #check if user already follows
                myselfs = dbfire.collection('Users').where('Email', '==', userEmail)
                for doc in myselfs.stream():
                    myselfs = doc.to_dict()
                myUsername = myselfs['userName']

                for key in userResult['FollowerNames']:
                    if(key == myUsername):
                        alreadyFollows = True
                    else:
                        alreadyFollows = False
                     
                print("HERE COMES THE USERNAME!")
                print(userResult)
                print("HERE COMES THE SESSION VARIABLE")
                print(session['userResults'])
                return render_template("userDisplay.html",  userResult = userResult, matching = matching, alreadyFollows = alreadyFollows, stockNames = session['stockNames'])
            else:
                print("Can't find user.")
                flash("User not found.")
                return render_template("social.html", stockNames = session['stockNames'])
        return render_template("social.html", stockNames = session['stockNames'])



#Miqdad Hafiz            
@app.route('/follow', methods = ["POST","GET"])
def follow():
    if 'user' in session:
        # First add 1 to followers number of user searched
        UserSearched = session['userResults']
        userNamed = UserSearched['userName']
        print(userNamed + " userNamed")
        
        
        userChange = dbfire.collection('Users').where('userName', '==', userNamed).get()
        for doc in userChange:
            key = doc.id
        print(key + " key1")
        userChanged = dbfire.collection('Users').document(key).update({'Followers':firestore.Increment(1)})

        # Second add 1 to following of the user (YOU)
        myself = dbfire.collection('Users').where('Email', '==', session['user']).get()
        for docus in myself:
            key2 = docus.id
            myself = docus.to_dict()
        print(key2 + " key2")
        myself2 = dbfire.collection('Users').document(key2).update({'Following': firestore.Increment(1)})
        myself2 = dbfire.collection('Users').document(key2).update({'FollowingNames': firestore.ArrayUnion([userNamed])})
        

        #Last add name to searched user follower array
        updateFollowArray = dbfire.collection('Users').where('userName', '==', userNamed).get()
        for docu in updateFollowArray:
            key3 = docu.id
        print(key3 + " key3")
        uName =  myself['userName']
        print("HERE COMES LAST PART")
        print(uName + " uName")
        updateFollowArray2 = dbfire.collection('Users').document(key3).update({'FollowerNames': firestore.ArrayUnion([uName])})
        flash("You have followed " + userNamed)
        return redirect(url_for("social"))
            


@app.route("/unfollow", methods = ['POST', 'GET'])
def unfollow():
    if 'user' in session:
        UserSearched = session['userResults']
        userNamed = UserSearched['userName']
        print(userNamed + " userNamed")
        
        userChange = dbfire.collection('Users').where('userName', '==', userNamed).get()
        for doc in userChange:
            key = doc.id
        print(key + " key")
        userchanged = dbfire.collection('Users').document(key).update({'Followers': firestore.Increment(-1)})

        myself = dbfire.collection('Users').where('Email', '==', session['user']).get()
        for doc1 in myself:
            key1 = doc1.id
        myself = doc1.to_dict()
        print(key1 + " key1")
        me = dbfire.collection('Users').document(key1).update({'Following': firestore.Increment(-1)})
        myself2 = dbfire.collection('Users').document(key1).update({'FollowingNames': firestore.ArrayRemove([userNamed])})
        
        followArray = dbfire.collection('Users').where('userName', '==', userNamed).get()
        for f in followArray:
            new = f.id
        print(new + " new")
        Names = myself['userName']
        newArray = dbfire.collection('Users').document(new).update({'FollowerNames': firestore.ArrayRemove([Names])})
        
        flash("You have unfollowed " + userNamed)
        return redirect(url_for("social"))

        
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

            # try: 
            
            user = authen.create_user_with_email_and_password(email, Password)
            authen.send_email_verification(user['idToken'])

                #User.registerUser(dbfire, UseN, email, NameU, user['localId'])
            dbfire.collection('Users').document(UseN).set({"Email": email, "Name":NameU, "UserID": user['localId'], "userName": UseN, "Followers": 0, "Following": 0, "FollowerNames": [""],"FollowingNames":[""], "experience": "", "QuizScore" : "0%"})
                #dbfire.collection('UsersFollowers').document(UseN).set({"Name": ""})
            flash("Account Created, you will now be redirected to verify your account" , "pass")
            flash("Account succesfully created, you may now login" , "pass")

            return redirect(url_for("login"))

            # except:
            #     flash("Invalid Registration" , "fail")
            #     return redirect(url_for("register"))
          
    return render_template('register.html')   


# ## Attempt on email verification function by Muneeb Khan (WIP!)
# @app.route('/verification', methods = ["POST" , "GET"])
# def verification():
#     if request.method == "POST":
#         try:
#             user = authen.send_email_verification(email['idToken'])
#             print("Verification sent")
#             return redirect(url_for("login"))

#         except:
#             print("Invalid token please try again!")
#             return redirect(url_for("verification"))

#     return render_template("verification.html")

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

#Author: Viraj Kadam
#Updated by Viraj and Muneeb
@app.route('/update', methods = ["POST", "GET"])
def update():
    if 'user' in session:
        if request.method == "POST":
            results = request.form
            newEmail = results['email']
            newUsername = results['Unames']
            experience = results["experience"]  
            
            checkName = dbfire.collection('Users').where('Email','==',session['user']).get()
            for docs in checkName:
                updatesInfo = docs.id
                checkName = docs.to_dict()

            goodName = newUsername
            
            if (len(experience) > 300):
                print("There is a 300 character limit")
                flash("There is a 300 character limit") #Adds experience to profile
                return render_template('update.html')
        
            elif (goodName == session['user']):
                print("Username is already taken. Please enter a valid username.")
                flash("Username is already taken. Please enter a valid username.") #check to see if new username is taken
                return render_template('update.html')
            
            else:
                dbfire.collection('Users').document(updatesInfo).update({"userName": newUsername, "Email": newEmail, "experience": experience})
                print("Account details updated")
                flash("Account details updated", "pass")

                return redirect(url_for("profile"))
        else:
            return render_template('update.html')

          
    return render_template('update.html')   
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

    stockNames = []
    for entry in dbfire.collection("StockSearchInfo").get():
        temp = entry.to_dict()
        stockNames.append(temp['name'])
    session['stockNames'] = stockNames
    print(stockNames) 
    
    return render_template("home.html",stockNames = session['stockNames'])

## Route for Home page - Muneeb Khan
@app.route("/home")
def home():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("home.html", person = person, stockNames = session['stockNames'])
    else:
        return render_template('home.html')

## Route for About us page - Muneeb Khan
@app.route("/aboutus")
def aboutus():
    if('user' in session): 
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("aboutus.html", person = person, stockNames = session['stockNames'])
    else:
        return render_template('aboutus.html')

## Route for Information Page - Muneeb Khan
@app.route("/information")
def information():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("information.html", person = person, stockNames = session['stockNames'])
    else:
        return render_template("information.html", stockNames = session['stockNames'])
    
@app.route("/StockDefinitions")
def StockDefinitions():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("StockDefinitions.html", person = person, stockNames = session['stockNames'])
    else:
        return render_template("StockDefinitions.html", stockNames = session['stockNames'])

# Route for Graph pictures page - Muneeb Khan
@app.route("/graphPictures")
def graphPictures():
    if('user' in session):
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("graphPictures.html", person = person, stockNames = session['stockNames'])
    else:
        return render_template("graphPictures.html", stockNames = session['stockNames'])

@app.route("/simulationSuggestion", methods=['POST', 'GET'])
def simSuggest():
    return -1

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
                        sim = Simulation(dbfire, session['user'], request.form['simStartDate'],
                            request.form['simEndDate'], request.form['initialCash'])
                        sim.createSim()
                        session['simName'] = sim.simName
                        
                        return redirect(url_for('.goToSimulation'))
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
            return render_template('stockSimForm.html', person=session['user'], stockNames = session['stockNames'])
    else:
        flash("Sorry you must be logged in to view that page.")
        return redirect(url_for("login"))
        
@app.route("/simulation", methods=['POST', 'GET'])
def goToSimulation():
    if ('user' in session):
        try:
            session['simulationFlag'] = 1
            sim = SimulationFactory(dbfire, session['user']).simulation
            session['initialCash'] = sim.initialCash
            session['simName'] = sim.simName
            if Simulation.ongoingCheck(dbfire, session['simName'], session['user']):
                sharesValue, currentCash = Simulation.getPortfolioValue(dbfire, session['simName'])
                sharesValue = float(sharesValue)
                currentCash = float(currentCash)
                session['currentCash'] = "%.2f" % round(currentCash,2)
                session['sharesValue'] = "%.2f" % round(sharesValue,2)
                session['portfolioValue'] = "%.2f" % round(currentCash + sharesValue, 2)
                session['currentChange'] = "%.2f" % round(currentCash + sharesValue - float(session['initialCash']), 2)
                tickers = []
                quantities = []
                profits = []
                sharesPrices = []
                currentPrices = []
                totalValue = []
                originalValue = []
                percentage = []
                volatility = []
                links = []
                buySell = []
                
                percentageTotal = 0
                for entry in Order.stocksBought(dbfire, session['simName']):
                    Portfolio = portfolio(dbfire, entry, session['user'], session['simName'])
                    if Portfolio.quantity != 0:
                        currentPrice = SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(entry)
                        tickers.append(entry)
                        quantities.append(Portfolio.quantity)
                        sharesPrices.append("$%.2f" % round(Portfolio.avgSharePrice,2))
                        currentPrices.append("$%.2f" % round(currentPrice, 2))
                        totalValue.append("$%.2f" % round(Portfolio.quantity*currentPrice, 2))
                        originalValue.append("$%.2f" % round(Portfolio.avgSharePrice*Portfolio.quantity, 2))
                        profits.append("%.2f" % round((Portfolio.quantity*currentPrice) - (Portfolio.avgSharePrice*Portfolio.quantity), 2))
                        percent = Portfolio.quantity*currentPrice / (currentCash+sharesValue) * 100
                        percentageTotal += percent
                        percentage.append("%.2f" % round(percent, 2))
                        volatility.append("%.2f" % round(Portfolio.volatility,2))
                        links.append(Portfolio.link)
                        buySell.append(Portfolio.newLink)
                session['stockPercentage'] = "%.2f" % round(percentageTotal, 2)
                session['cashPercentage'] = "%.2f" % round(currentCash / (sharesValue + currentCash) * 100, 2)
                session['percentGrowth'] = "%.2f" % round((currentCash + sharesValue - float(session['initialCash']))/float(session['initialCash']) * 100, 2)

                return render_template('simulation.html', person=session['user'], tickers=tickers, 
                quantities=quantities, profits=profits, sharesPrices=sharesPrices,
                currentPrices=currentPrices, totalValue=totalValue, originalValue=originalValue,
                percentage=percentage, links=links, buySell = buySell)  
            else:
                return redirect(url_for('.finishSimulation'))
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

@app.route("/simulationHistory")
def simlists():
    if ('user' in session):
        sims, dates, scores, links = Simulation.listSims(dbfire, session['user'])             
        return render_template('simulationHistory.html', person = session['user'],sims = sims, 
        dates = dates, scores = scores, links=links, stockNames = session['stockNames'])

#@app.route("/buySell/<simName>")
#def buySell(simName):
#    if 'user' in session:
#        return redirect(url_for('.ordeForm'))

@app.route("/orderForm", methods=['POST', 'GET'])
def orderFormFill():
    session['option'] = request.form['option']
    if session['option'] == 'Buy':
        session['optionType'] = 0
    else:
        session['optionType'] = 1
    session['currentPrice'] = "%.2f" % round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(session['ticker']), 2)
    session['currentAmount'] = SimulationFactory(dbfire, session['user']).simulation.amountOwned(session['ticker'])
    return render_template('orderForm.html', option=session['option'], stockNames = session['stockNames'])

@app.route("/sellTaxLot/<orderID>")
def sellTaxLot(orderID):
    if 'user' in session:
        order = dbfire.collection('Orders').document(orderID).get().to_dict()
        session['orderID'] = orderID
        session['option'] = 'Sell'
        session['optionType'] = 1
        session['currentPrice'] = "%.2f" % round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(session['ticker']), 2)
        if order.get('newQuantity') != None:
            session['stockQuantity'] = order['newQuantity']
        else:
            session['stockQuantity'] = order['quantity']
        session['currentAmount'] = session['stockQuantity']
        session['orderPrice'] = "%.2f" % round(float(session['stockQuantity']) * float(session['currentPrice']), 2)
        return render_template('orderConfirmation.html')
    else: return redirect(url_for('fourOhFour'))

@app.route("/sellTaxLot/taxLotSellConfirm", methods=['POST', 'GET'])
def taxLotSellConfirm():
    if 'user' in session:
        order = Order.sellTaxLot(dbfire, session['user'], session['simName'], session['orderID'])
        return redirect(url_for('.goToSimulation'))
    else: return redirect(url_for('fourOhFour'))

#@app.route("/orderCreate", methods=['POST', 'GET'])
#def orderCreate():
#    return render_template('orderConfirmation.html', option=session['option'])

@app.route("/orderConfirm", methods=['POST', 'GET'])
def orderConfirm():
    if request.form['stockQuantity'].isnumeric():
        session['orderQuantity'] = request.form['stockQuantity']
        session['orderPrice'] = "%.2f" % round(float(session['orderQuantity']) * float(session['currentPrice']), 2)
        order = Order(dbfire, session['simName'], session['ticker'], 
                        session['option'], session['orderQuantity'], session['currentPrice'])
        if session['option'] == 'Buy':
            flag = order.buyOrder()
        else:
            flag = order.sellOrder()
        if flag == 1:
            flash("Order Complete!")  

            return redirect(url_for('.goToSimulation'))

        elif session['option'] == 'Buy' and flag == -1:
            flash("Insufficient funds to complete purchase")
            return render_template('orderForm.html', option=session['option'])
        elif session['option'] == 'Sell' and flag == -1:
            flash("Insufficient shares to complete sale")
            return render_template('orderForm.html', option=session['option'])
    else:
        flash("Please enter a valid quantity amount")
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
                check = StockData.stockSearch(dbfire, request.form["searchTerm"], session['simName'])
                if check[0]:
                    print(check)
                    if session['simulationFlag'] == 1:
                        return redirect(url_for('displayStock', ticker=check[1], timespan="hourly", startDate=''))
                    else:
                        return redirect(url_for('stockSimFormFunction'))
                else:
                    return redirect(url_for('stockListing'))
        except KeyError:
            print("KeyError occured: stockSearch")
            return redirect(url_for('fourOhFour'))
    else:
        flash("Sorry you must be logged in to view that page.")
        return redirect(url_for("login"))


# Function for Stock search suggestions list by Muneeb Khan
@app.route('/_stockSearchSuggestions', methods=['POST','GET'])
def stockSearchSuggestions():
    if ('user' in session):
        # Will get the users input
        if request.method == 'GET':
            stockNames = []
            # This will loop through the stock names from firebase - Muneeb Khan
            for entry in dbfire.collection("StockSearchInfo").get():
                temp = entry.to_dict()
                stockNames.append(temp['name'])

            session['stockNames'] = stockNames # This will store the names in session list (Updated from Ian Mcnulty)
            print(stockNames) 
            return render_template("home.html", stockNames = session['stockNames'])

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
@app.route('/displayStock')
def displayStock():
    startDate = request.args['startDate']
    ticker = request.args['ticker']
    timespan = request.args['timespan']
    session['ticker'] = ticker
    global stock
    if Simulation.ongoingCheck(dbfire, session['simName'], session['user']):
        stockData = SimulationFactory(dbfire, session['user']).simulation.retrieveStock(ticker)
        BasisData = dbfire.collection('Stocks').document(session['ticker']).get().to_dict()
        final = SimulationFactory(dbfire, session['user']).simulation.whatTimeIsItRightNow()
        session['currentPrice'] = "%.2f" % round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(session['ticker']), 2)
        existenceFlag = True
        for entry in stockData:
            temp = entry.to_dict()
            if temp.get('unavailable') != None:
                existenceFlag = False
        if existenceFlag:
            if timespan == 'hourly':
                for entry in stockData:
                    stock = entry.to_dict()
                if stock != -1:
                    session['currentYear'] = str(stock['dates'][final][0:4])
                    session['currentMonth'] = str(stock['dates'][final][5:7])
                    session['currentDay'] = str(stock['dates'][final][8:10])
                    dates = []
                    prices = []
                    avgPrice = []
                    for i in range(0, final):
                        avgPrice.append(stock['prices'][i])
                        if i % 6 == 1:
                            prices.append(mean(avgPrice))
                            dates.append(stock['dates'][i-1])
                    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=prices)
            elif timespan == 'daily' or timespan == 'weekly' or timespan == 'monthly':
                if timespan == 'daily':
                    mod = 40
                elif timespan == 'weekly':
                    mod = 40*7
                    BasisMod = 7
                for entry in stockData:
                    stock = entry.to_dict()
                if stock != -1:
                    session['currentYear'] = str(stock['dates'][final][0:4])
                    session['currentMonth'] = str(stock['dates'][final][5:7])
                    session['currentDay'] = str(stock['dates'][final][8:10])
                    dates = []
                    prices = []
                    avgPrice = []
                    b = BasisData['daily']['dates'].index(stock['dates'][0][0:10])
                    if startDate != '':
                        tempArr = np.array(BasisData['daily']['dates'])
                        startLoc = np.where(tempArr == startDate)   
                        if startLoc[0].size == 0:
                            tempDate = startDate
                            month = int(tempDate[5:7])
                            day = int(tempDate[8:10])
                            year = int(tempDate[0:4])
                            while startLoc[0].size == 0:
                                day += 1
                                if day >= DAYS_IN_MONTH[month]:
                                    month += 1
                                    if month >= 12:
                                        month = 1
                                        year += 1
                                    day = 1
                                if month < 10:
                                    strMonth = "0" + str(month)       
                                else: 
                                    strMonth = str(month)
                                if day < 10:
                                    strDay = "0" + str(day)       
                                else: 
                                    strDay = str(day)
                                strYear = str(year)
                                startLoc = np.where(tempArr == (strYear + "-" + strMonth + "-" + strDay))
                        a = startLoc[0][0]
                    else:
                        a = b - 30
                    for i in range(a, b):
                        if timespan == 'monthly':
                            BasisMod = 30
                        if timespan == 'daily':
                            prices.append(float(BasisData['daily']['opens'][i]))
                            dates.append(BasisData['daily']['dates'][i])
                        else:
                            if i % BasisMod == 1:
                                prices.append(float(BasisData['daily']['opens'][i]))
                                dates.append(BasisData['daily']['dates'][i])
                    for i in range(0, final):
                        avgPrice.append(stock['prices'][i])
                        if timespan == 'monthly':
                            mod = 40*7*int(stock['dates'][i][5:7])
                        if i % mod == 1:
                            prices.append(round(mean(avgPrice), 2))
                            dates.append(stock['dates'][i][0:10])
                            avgPrice = []
                        #    if int(stock['dates'][i][11:13]) == 9:
                        #        mod = 6
                    session['currentPrice'] = "%.2f" % round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(stock['ticker']), 2)
                    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=prices, stockNames = session['stockNames'])

            elif timespan == '1minute' or timespan == '5minute':
                for entry in stockData:
                    stock = entry.to_dict()
                if stock != -1:
                    session['currentYear'] = str(stock['dates'][final][0:4])
                    session['currentMonth'] = str(stock['dates'][final][5:7])
                    session['currentDay'] = str(stock['dates'][final][8:10])
                    dates = []
                    prices = []
                    for i in range(1, final):
                        #if timespan == '5minute':
                        #    tempInterp = np.interp(range(0,3),[0, 2],[stock['prices'][i-1], stock['prices'][i]])
                        #    for element in tempInterp:
                        #        element += (np.random.randn() + np.std([stock['prices'][i-1], stock['prices'][i]]))/50
                        #        prices.append(element)
                        #    # 15 = index of minute
                        #    tempDate1 = list(stock['dates'][i])
                        #    for j in range(1,3):
                        #        tempDate2 = tempDate1
                        #        tempDate2[15] = str((j*5)%10)
                        #        if i % 6 != 0:
                        #            tempDate2 = tempDate2[11:19]
                        #        dates.append("".join(tempDate2))
                        if timespan == '1minute':
                            tempInterp = np.interp(range(0,11),[0, 10],[stock['prices'][i-1], stock['prices'][i]])
                            for element in tempInterp:
                                element += (np.random.randn() + np.std([stock['prices'][i-1], stock['prices'][i]]))/50
                                prices.append(element)
                            tempDate1 = list(stock['dates'][i])
                            for j in range(0,10):
                                tempDate2 = tempDate1
                                tempDate2[15] = str(j)
                                if i % 30 != 0:
                                    tempDate2 = tempDate2[11:19]
                                dates.append("".join(tempDate2))
                    session['currentPrice'] = "%.2f" % round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(stock['ticker']), 2)
                    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=prices, stockNames = session['stockNames'])
            else:
                for entry in stockData:
                    stock = entry.to_dict()
                if stock != -1:
                    session['currentYear'] = str(stock['dates'][final][0:4])
                    session['currentMonth'] = str(stock['dates'][final][5:7])
                    session['currentDay'] = str(stock['dates'][final][8:10])                    
                    dates = []
                    prices = []
                    for i in range(0, final):
                        dates.append(stock['dates'][i])
                        prices.append(stock['prices'][i])
                    session['currentPrice'] = "%.2f" % round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(stock['ticker']), 2)
                    return render_template('stockDisplay.html', stock=stock, dates=dates, avgs=prices, stockNames = session['stockNames'])
        else:
            return redirect(url_for('fourOhFour'))
    else:
        return redirect(url_for('finishSimulation'))

## changeStockView
#   Description: Retrieves data from stockView page to determine how to change
#   the view of the stock (monthly instead of weekly, change date range, etc)
#
#   Author: Ian McNulty
@app.route('/changeView', methods=['POST'])
def changeStockView():
    if request.method == 'POST':
       
        return redirect(url_for('.displayStock', ticker=session['ticker'], timespan=request.form['timespan'], startDate=request.form['startDate']))
    return -1

@app.route('/stockList', methods=['POST','GET'])
def stockListing():
    if session['simulationFlag'] == 1:
        sim = SimulationFactory(dbfire, session['user']).simulation
        session['simName'] = sim.simName
        tickers, prices, links, names = Simulation.getAvailableStockList(dbfire, session['simName'], session['user'])
        return render_template('stockList.html', person=session['user'], tickers=tickers, currentPrices=prices, links=links, names=names, stockNames = session['stockNames'])
    else:
        return redirect(url_for('stockSimFormFunction'))

## stockSim
#   Description: Brings the logged in user to the stock sim start page, if the user
#   isn't logged in, a 404 page error is given.
#
#   Author: Ian McNulty
@app.route("/stockSimForm", methods=['POST', 'GET'])
def stockSimFormFunction():
    if 'user' in session:
        return render_template('stockSimForm.html', person=session['user'], stockNames = session['stockNames'])
    else:
        return redirect(url_for('fourOhFour'))

@app.route("/stockAvailability",methods=['POST'])
def stockAvailability():
    if request.method == 'POST':
        return redirect(url_for('stockDisplay.html',ticker=session['ticker'],startDate="2021-09-08",endDate="2022-09-19",timespan="daily"))

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
        buySellButtons = []
        for entry in Order.stocksBought(dbfire,session['simName']):
            Portfolio = portfolio(dbfire,entry,session['user'],session['simName'])
            if Portfolio.quantity != 0:
                buySellButtons.append(Portfolio.newLink)

        return render_template('orderList.html',person=session['user'],buys=orderlist['buyOrSell'].to_list(), dates=orderlist['dayOfPurchase'].to_list(),
        tickers=orderlist['ticker'].to_list(), quantities=orderlist['quantity'].to_list(), prices=orderlist['totalPrice'].to_list(), partiallySold=orderlist['partiallySold'].to_list(), 
        profits=orderlist['profit'].to_list(), links=orderlist['links'].to_list(), stockNames = session['stockNames'])

@app.route("/orderHist/<simName>")
def orderHist(simName):
    if ('user' in session):
        return redirect(url_for('.orderHistory', simName=simName))

@app.route("/orderHistory")
def orderHistory():
    simName = request.args['simName']
    orderlist = Order.orderList(dbfire, simName) # This will have the username show on webpage when logged in - Muneeb Khan

    return render_template('orderHistory.html',person=session['user'],buys=orderlist['buyOrSell'].to_list(), dates=orderlist['dayOfPurchase'].to_list(),
    tickers=orderlist['ticker'].to_list(), quantities=orderlist['quantity'].to_list(), prices=orderlist['totalPrice'].to_list(), stockNames = session['stockNames'])       

## 
@app.route('/404Error')
def fourOhFour():
    return render_template('404Error.html',person = session['user'], stockNames = session['stockNames'])
    
#@app.route('/startSimulation')
#def portfolioGraph():
#    if 'user' in session:

## Route for Quiz selection page - Muneeb Khan
@app.route("/quizselection")
def quizselection():
    if('user' in session): 
        person = dbfire.collection('Users').where('Email', '==', session['user']) # This will have the username show on webpage when logged in - Muneeb Khan

        for x in person.get():
            person = x.to_dict()

        return render_template("quizselection.html", person = person, stockNames = session['stockNames'])
    else:
        flash("Sorry you must be logged in to take the quiz.")
        return redirect(url_for("login"))

# Submission check route for Quiz by Ian Mcnulty
# Updates by Muneeb Khan
@app.route('/quizSubmit', methods = ['GET', 'POST'])
def quizSubmit():
    quiz = Quiz(dbfire,'Quiz1',session['user'])
    answers = []
    ids = quiz.questions['id']
    for i in range(10):
        temp = "choices" + str(i)
        if request.form.get(temp) != None:
            answers.append(request.form[temp])
            quiz.answerQuestion(ids[i], request.form[temp])
        else: 
            answers.append('f')
            quiz.answerQuestion(ids[i], 'f')

    score = quiz.scoreCalc()
    if score >= 7:
        ## This will store the users quiz score on Firebase - Muneeb Khan
        yourscore = dbfire.collection('Users').where('Email', '==', session['user']).get()
        for scores in yourscore:
            updatescore = scores.id
            yourscore = scores.to_dict()
        dbfire.collection('Users').document(updatescore).update({'QuizScore': str(score*10) + "%"}) # Convert users score to percentage - Muneeb Khan
        flash("Congratulations! You passed the Quiz, your score was " + str(score) + "/10" + 
        " You are now ready to invest, please click the start simulation button above to start investing." +
        "Correct answers were: " +
        "1 B " + 
        "2 A " +
        "3 B " +
        "4 A " +
        "5 C " +
        "6 C " +
        "7 A " +
        "8 C " +
        "9 B " +
        "10 A ")
        return redirect(url_for('information', person = session['user']))
    else:
        ## This will store the users quiz score on Firebase - Muneeb Khan
        yourscore = dbfire.collection('Users').where('Email', '==', session['user']).get()
        for scores in yourscore:
            updatescore = scores.id
            yourscore = scores.to_dict()
        dbfire.collection('Users').document(updatescore).update({'QuizScore': str(score*10) + "%"}) # Convert users score to percentage - Muneeb Khan
        flash("Sorry! You did not pass the Quiz, your score was " + str(score) + "/10," + 
        " You need to score at least a 7/10 to pass. Please try again."  + 
        "Correct answers were: " +
        "1 B " + 
        "2 A " +
        "3 B " +
        "4 A " +
        "5 C " +
        "6 C " +
        "7 A " +
        "8 C " +
        "9 B " +
        "10 A ")
        return redirect(url_for('information', person = session['user']))


# Quiz page route by Muneeb Khan
@app.route('/quiz', methods =['GET','POST'])
def quizpage():
    if ('user' in session):
        quizID = 'Quiz1'
        quiz = Quiz(dbfire,quizID,session['user'])
        questions = quiz.questions['text']
        answers = quiz.questions['answers']
        answers1 = [answers[0]]
        answers2 = [answers[1]]
        answers3 = [answers[2]]
        answers4 = [answers[3]]
        answers5 = [answers[4]]
        answers6 = [answers[5]]
        answers7 = [answers[6]]
        answers8 = [answers[7]]
        answers9 = [answers[8]]
        answers10 = [answers[9]]


        if (request.method == 'POST'):
            
            choiceA = request.args['a']
            choiceB = request.args['b']
            choiceC = request.args['c']
            submitButton = request.args['submitButton']

            if request.method == choiceA:
                return Quiz.answerQuestion(dbfire,session['user'],choiceA)
            elif request.method == choiceB:
                return Quiz.answerQuestion(dbfire,session['user'],choiceB)
            elif request.method == choiceC:
                return Quiz.answerQuestion(dbfire,session['user'],choiceC)
            elif request.method == submitButton:
                return Quiz.submitScore(dbfire)
            

        return render_template('quiz.html',quiz = quiz, questions = questions, answers = answers,
        answers1 = answers1, answers2 = answers2, answers3 = answers3, answers4 = answers4, answers5 = answers5,
        answers6 = answers6, answers7 = answers7, answers8 = answers8, answers9 = answers9, answers10 =answers10, stockNames = session['stockNames'])
                   
    else:
        flash("Sorry you must be logged in to take the quiz.")
        return redirect(url_for("login"))

if __name__ == '__main__':
    app.run(debug=True)
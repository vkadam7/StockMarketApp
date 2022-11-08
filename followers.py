#Author: Viraj Kadam 
#Followers feature: Allows user to search, follow, and unfollow different users
from this import d
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import pyrebase
from google.cloud import firestore
from stockSim import User
from re import search

class UserInfo():
    def __init__(self, db, username):
        self.db = db
        self.username = username
        self.userDataDocument = self.retrieve()
        if self.userDataDocument != 'This data entry does not exist':
            self.email = self.userDataDocument['Email']
            self.userID = self.userDataDocument['UserID']
            self.description = self.userDataDocument['Description']
            self.picture = self.userDataDocument['Picture']
            self.experience = self.userDataDocument['Experience']
        else:
            print("This user does not exist")
            
    def retrieveuserProfile(self):
        profile = self.db.collection('Users').document(self.username)
        return profile
    
    
    #Search for a user
    def userSearch(db, searchTerm):
        tempData1 = db.collection('Users').document(searchTerm).get() 
        if tempData1 != None:
            return True, searchTerm

        userssDB = db.collection('Users')
        for entry in userssDB.stream():
            temp = entry.to_dict()
            name = temp['Name'].lower()
            username = temp['username'].lower()
            tempSearchTerm = searchTerm.lower()
            if tempSearchTerm == name:
                return True, name.upper()
            if tempSearchTerm in username:
                return True, username.upper()

        return False, -1
    
class FollowUnfollow:
    def __init__(self, db, followOrUnfollow, user, name):
        self.db = db
        self.option = self.followOrUnfollow
        self.user = user
        self.name = name
        
        
    
    
    def followOption(self):
        if self.option == 'Follow':
            if self.doTheyhaveAnaccount() == True:
                if self.doTheyFollow() == False:
                    userName = self.user 
                    data ={
                        'name': self.name
                    }
                    for follower in data:
                        doc_ref = self.db.collection('UsersFollowers').document(userName).set(data)
                                    
    def unfollowOption(self):
        if self.option == 'Unfollow':
            if self.doTheyhaveAnaccount() == True:
                if self.doTheyFollow() == True:
                    userName = self.user
                    data = {
                        'name': self.name
                    }
                    for follower in data:
                        doc_ref = self.db.collection('UserFollowers').document(userName).get(data)
                        
    
    def followList(self):
        followList = []
        followList = self.db.collection('Users').document('followList')
        follow_ref = self.db.collection(u'Users').document(u'followList')
        doc = follow_ref.get()
        print(doc.to_dict())
    
    
    def doTheyhaveAnaccount(self, db, user):
        accountFlag = False
        tempdata = self.db.collection('Users').document('userName')
        doc_ref =  self.db.collection('Users').document('userName')
        temp = tempdata.get()
        if temp.exists():
            accountFlag = True
            return accountFlag
        else:
            print("User does not have an account in StockSim")
       
        
    
    def doTheyFollow(self):
        followingFlag = False
        numfollowing = 0
        for person in self.db.collection('Users').document('followingList').stream():
            temp = person.to_dict()
            if temp.get('username') != None:
                numfollowing = int(temp['followingList'])
                followingFlag = True
            else:
                followingFlag = False
        print(numfollowing)

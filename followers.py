#Author: Viraj Kadam 
#Followers feature: Allows user to search, follow, and unfollow different users
from this import d
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import pyrebase
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
    def __init__(self, db, followOrUnfollow, user):
        self.db = db
        self.option = self.followOrUnfollow
        self.user = user
        
        
    
    
    def followOption(self):
        following = []
        if self.option == 'Follow':
            if self.doTheyhaveAnaccount() == True:
                if self.doTheyFollow() == False:
                    for request in self.db.collection('Users').where('Name', '==', user1).stream():
                     temp = request.to_dict()
                     following.append(temp['followingList'])
        
        print(following)
        
                
                
                
    def unfollowOption(self):
        following = []
        if self.option == 'Unfollow':
            if self.doTheyhaveAnaccount() == True:
                if self.doTheyFollow() == True:
                    for unfollow in self.db.collection('Users').where('Name', '==', user1).stream():
                        temp = unfollow.to_dict()
                        following.remove(temp['followingList'])
                        
    
    def followList(self):
        followList = []
        
    
    
    def doTheyhaveAnaccount(self, db, user):
        
        if UserInfo.userSearch(db, user):
            return
        
    
    def doTheyFollow(self):
        followFlag = False
        followingFlag = False
        
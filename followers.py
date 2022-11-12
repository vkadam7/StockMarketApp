#Author: Viraj Kadam 
#Followers feature: Allows user to search, follow, and unfollow different users
from this import d
import main
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import pyrebase
from google.cloud import firestore
from stockSim import User
from re import search
import pandas as pd

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
    def __init__(self, db, followOrUnfollow, user, names, num):
        self.db = db
        self.option = self.followOrUnfollow
        self.user = user
        self.name = names
        self.num = num
        
    def followOption(self):
        if self.option == 'Follow':
            if self.doTheyhaveAnaccount() == True: #Checks if user has an account
                if self.doTheyFollow() == False: #Checks if the user already follows that person
                    userName = self.user 
                    data ={
                        'names': self.name
                    }
                    for follower in data:
                        doc_ref = self.db.collection('UsersFollowers').where('userName', '==', userName).set(data)
        return -1
                                    
    def unfollowOption(self):
        if self.option == 'Unfollow':
            if self.doTheyhaveAnaccount() == True:
                if self.doTheyFollow() == True:
                    userName = self.user
                    data = {
                        'names': self.name
                    }
                    doc_ref = self.db.collection('UserFollowers').where('userName', '==', userName).get(data)
                    for follower in doc_ref.stream():
                        follower_ref = self.db.collection('UserFollowers').where('userName', '==', userName)
                        follower_ref.update({u'names': firestore.DELETE_FIELD})
        return -1
                    
                        
    
    def retrievefollowList(self, user):
       followersList = []
       peopleFollowed = 0
       userName = self.user
       for doc in self.db.collection('UserFollowers').where('userName', '==', userName).stream():
           temp = doc.to_dict()
           followersList.append([temp['names']])
       df = pd.DataFrame(followersList, columns=['names'])
       return df 
           
       
    def doTheyFollow(self, db, user):
        followingFlag = False
        for person in self.db.collection('UserFollowers').document('userName', '==', user).stream():
            temp = person.to_dict()
            if temp.get('userName') != None:
                numfollowing = int(temp['followingList'])
                followingFlag = True
            else:
                followingFlag = False
    
    
    def countFollowers(self, db, user, name):
        #numofFollowers = 0
        #for person in self.db.collection('UserFollowers').where('userName', '==', user).stream():
        #    temp = person.to_dict()
        #    count = len(temp)
        #numofFollowers = count
        #return numofFollowers 
         
        numofFollowers = len(self.retrievefollowList)
        return numofFollowers  
        
        
        
        
        
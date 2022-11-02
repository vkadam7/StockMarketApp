#Author: Viraj Kadam 
#Followers feature: Allows user to search, follow, and unfollow different users
from this import d
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import pyrebase



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
    def __init__(self, db, followOrUnfollow, user1, user2):
        self.db = db
        self.option = self.followOrUnfollow
        self.user1 = user1
        self.user2 = user2
        
    
    
    def followOption(self, db, user1, user2):
        if self.option == 'Follow':
            if self.doTheyhaveAnaccount() == True:
                if doTheyFollow() == False:
                    return
                
                
                
    def unfollowOption(self, db, user1, user2):
        if self.option == 'Unfollow':
            if self.doTheyFollow() == True:
                remove = self.db.collection('')
                
                
            
    def doTheyhaveAnaccount(self):
        return
    
    
    def doTheyFollow(self):
        followCheck = self.db.collection('Following').collection('users').get()
        followingCheck = self.db.collection('Followers').collection('users').get()
        if followCheck == followCheck:
            return True
        else:
            return False


class Recommendation:
    def __init__(self, db, recommend, ):
        return
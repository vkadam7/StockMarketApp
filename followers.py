#Author: Viraj Kadam 
#Followers feature: Allows user to search, follow, and unfollow different users
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
import pyrebase



class Followers():
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
            username = temp['usernam'].lower()
            tempSearchTerm = searchTerm.lower()
            if tempSearchTerm == name:
                return True, name.upper()
            if tempSearchTerm in username:
                return True, username.upper()

        return False, -1
    
    
    
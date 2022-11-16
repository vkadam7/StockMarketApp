#Author: Viraj Kadam 
#Followers feature: Allows user to search, follow, and unfollow different users
from this import d
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import ArrayUnion, ArrayRemove
import pyrebase
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

class FollowUnfollow:
    def __init__(self, db, followOrUnfollow, user1, user2, num):
        self.db = db
        self.option = followOrUnfollow
        self.user1 = user1
        self.user2 = user2
        self.num = num
        
    def followOption(self, db, user1, user2):
        data = db.collection('Users').document('username').get()
        for user in db.collection('Users').document('userName').stream():
             user1 = user.to_dict()
             return user1
        if self.option == 'Follow':
            if self.doTheyFollow() == False:
                user2 = data['name']
                searchTerm = db.collection('Users').where('userName', '==', user2)
                for docs in searchTerm.stream():
                    user2 = searchTerm.to_dict()
                followRequestName = user2['names']
                db.collection('UsersFollowers').document(user1).add({"names": followRequestName})
                
            else: 
                print("You already follow this user")        
        #if self.option == 'Follow':
        #      userName = db.collection('Users').document('userName').get()
        #        data['names'] = self.user2
        #        doc_ref = self.db.collection('UsersFollowers').add(data)
        #        for follower in doc_ref.stream():
        #             follower_ref = doc_ref
        #             follower_ref.update({u'names': firestore.ArrayUnion([data])})
        #        return 1
        #    else:
        #        return -1
        
                                    
    def unfollowOption(self, db):
        data = db.collection('Users').document('username').get()
        for user in db.collection('Users').document('userName').stream():
             user1 = user.to_dict()
             return user1
        if self.option =='Unfollow':
            if self.doTheyFollow() == True:
                user2 = db.collection('UsersFollowers').document(user1).get()
                for doc in user2.stream():
                    unfollow = user2.to_dict()
                unfollowRequest = unfollow['names']
                unfollow_ref =  db.collection('UserFollowers').document(user1).where('names', '==', user2).delete()
            else:
                print("You do not follow this user")                    
        #if self.option == 'Unfollow':
        #    if self.doTheyFollow() == True:
        #        userName = self.user1
        #        data = {
        #            'names': [self.user2]
        #        }
        #       doc_ref = self.db.collection('UserFollowers').where('userName', '==', userName).get(data)
         #       for follower in doc_ref.stream():
         #           follower_ref = doc_ref
         #           follower_ref.update({'names': firestore.ArrayRemove([self.user2])})
         #      return 1
          #  else:
           #     return -1
        
                    
                        
    
    def retrievefollowList(self, user1):
       followersList = []
       peopleFollowed = 0 
       userName = self.user1
       for doc in self.db.collection('UserFollowers').where('userName', '==', userName).stream():
           temp = doc.to_dict()
           followersList.append([temp['names']])
       df = pd.DataFrame(followersList, columns=['names'])
       return df 
    
    
    def countFollowers(self, db, user1, user2):
        #numofFollowers = 0
        #for person in self.db.collection('UserFollowers').where('userName', '==', user).stream():
        #    temp = person.to_dict()
        #    count = len(temp)
        #numofFollowers = count
        #return numofFollowers 
        data = db.collection('Users').document(self.user1).get().to_dict()
        userName = self.user
        num = pd.value_counts(self.retrievefollowList(userName))
        numFollowers = num 
        data['followers'] = numFollowers
        return self.db.collection('Users').where('userName', '==', userName).add({"followers": numFollowers})
        
        #numofFollowers = len(self.retrievefollowList)
        #return numofFollowers  
        
       
    def doTheyFollow(self, db, user1, user2):
        followingFlag = False
        for person in self.db.collection('UserFollowers').where('userName', '==', user1).stream():
            temp = person.to_dict()
            if temp.get('userName') != None:
                followingFlag = True
                return followingFlag
            else:
                followingFlag = False
                return followingFlag
        
        
        
        
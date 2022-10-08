from main import StockData
import pandas as pd
import numpy as np
from Order import buyOrder
import pyrebase
from firebase_admin import db
from main import firebase_admin, firebase


db = firebase.databse()
#Dashboard will include basic summary of user in game, such as user info, profit, and number of stocks owned.
# This will be directly connected to the porfolio. 
class dashboaard():
    
    def __init__(self, db, user, startDate, endDate, ):
        self.firebase = db
        self.data = self.retrieve(self.ticker)
        if self.data != 'This data entry does not exist':
            self.name = self.data['name']
        else:
            print(self.data)
        
    
    
    def UserInfo(self,username, name, db):
       username = self.db.child('Users').child('Username').get().val()
       name = self.db.child('Users').child('Name').get().val()
       
       
        
        
        
        

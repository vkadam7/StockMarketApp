from main import StockData
import pandas as pd
import numpy as np
from Order import buyOrder
import pyrebase


#Dashboard will include basic summary of user in game, such as user info, profit, and number of stocks owned.
# This will be directly connected to the porfolio. 
class dashboaard():
    def UserInfo(username, db, self):
        str  = username
        

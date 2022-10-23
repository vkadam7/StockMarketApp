#Author: Viraj Kadam
#initial portfolio python file, will need to fix some more
from cgi import print_exception
from lib2to3.pgen2.token import CIRCUMFLEXEQUAL
from re import I
from main import firebase, app
import csv
import pyrebase
import numpy as np
import pandas as pd
import Order
from Order import buyOrder
import requests
import StockData
import datetime as dt
from datetime import date
from pypfopt.discrete_allocation import DiscreteAllocation
from pypfopt import expected_returns
import matplotlib.pyplot as plt


db = firebase.database()

class portfolio:
    def __init__(self, db, stock, user, index, buyOrSell, quantity, stockPrice, startDate, endDate, initialCash):
        self.firebase = db
        self.stock = stock
        self.user = user
        self.startDate = startDate
        self.quantity = quantity
        self.initialCash = initialCash
        self.stockPrice = stockPrice
        return -1
    
    #def displayPortfolio(self):
     #   count = len(self.db.collection('Simulations').get(id))
    #  simName = "Sim" + str(count+1)
    # self.simName = simName
    #    data = {
     #           'ongoing': True,
      #          'user': self.user.email,
       #         'startDate': self.startDate,
        #       'initialCash': self.initialCash,
         #       'currentCash': self.initialCash,
          #      'score': 0,
         #       'Orders': [],
          #      'profit': 0
           # }
        #self.db.collection('Simulations').document(simName).set(data)
        
    
    def retrieve(self, id):
        stockRetrieved = self.db.collection('Simulations').document(simName).document('intradayStockDataTableKey').get()
        return stockRetrieved
        

    #Retrieves the number of shares owned by the user, to be implemented once buy and sell features are finished. Will be coded in line with
    #those feaures.
    
   # def get_shares_owned(self, db, stock, user, quantity, stockPrice):
    #   self.stock = stock
     #   data = {'name': self.name,
      #          'dayOfPurchase': self.dayOfPurchase,
       #         'quantity': self.quantity,
        #        'avgStockPrice': self.avgStockPrice,
         #       'totalPrice': self.totalPrice}
        
        #self.db.collection('Stocks').document('name').get()
        
        #return -1
        
        

    #Returns profit from the simulator(Need to test and fix if needed )
    def get_profit(self, db, stock, quantity, avgstockPrice):
        data = {'name' : self.name, 
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice}
        profit = 0
        tempPrice = self.db.collection('Simulations').document('daily').document('closes').get()
        quantity = self.db.collection('Simulations').document('daily').document('volume').get()
        profit += tempPrice * quantity
        return profit
    
    #Displays amount of shares owned (To also be implemented later)
    def weight(self, db, stock):
        share = [self.quantity]
        max_share = 1
        for share in max_share:
            if(self.quantity <= max_share and self.quantity >= 0):
                return share[self.quantity]
            else:
                return -1   
        
    #Fixed this section to account for gains or losses, need to test to check if everything is correct  
    def GainorLoss(self, db, stock, quanity, stockPrice, simName=""):
        tempData = self.db.collection('Simulations').document(self.sim).document('Orders').get()
        data = {'name': self.name, 
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice, 
                }
        if quanity > 0:
            if totalGain > CurrentPrice:
                tempPrice = self.db.collection('Simulations').document(simName).document('Stocks').document('prices').get()
                #Need to fix this function
                #CurrentPrice = self.db.collection('Stocks').document('daily').document('closes').get()
                CurrentPrice = self.db.collection('Simulations').document(simName).document('currentCash').document('prices').get()
                #day = self.db.collection('Stocks').document('daily').document('dates').get()
                day = self.db.collection('IntradayStockData').document('dates').get()
                for CurrentPrice in day :
                    netGainorLoss = (CurrentPrice[day + 1] - tempPrice[day]) / (tempPrice[day]) * 100
                    if netGainorLoss > CurrentPrice:
                        netLoss = "-" + netGainorLoss
                        print("Net loss" + netLoss )
                        return netLoss

                    else:
                        netGain = netGainorLoss
                        print("Net Gain: " + netGain)
                        return netGain
        
        return -1
                           
     #Determines how much money the user has left to spend in the game. Need to include an if statement for when the user sells stocks      
    def funds_remaining(self, initialAmount, finalAmount):
        finalAmount = 0
        fundsUsed = 0
        fundsRemainiing = 0
        quantity = 0
        tempPrice = self.db.collection('Stocks').document('daily').document('closes').get()
        data = {'name': self.name,
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice, 
                'startDate': self.startDate,
                'endDate': self.endDate,
                'initialCash': self.initialCash,
                'currentCash': 0,
                'score': 0,
                'Orders': []  
        }
       
        if data ['currentCash'] == data['initialCash']:
           return data['currentCash']
        elif data['currentCash'] > data['initialCash']:
            fundsUsed = data['currentCash'] - data['initialCash']
            fundsRemainiing = fundsUsed
            return fundsRemainiing
        else: 
            return -1
        
    #Edited returns feature
    def returns(self, quantity, avgStockPrice, AdjustClose):
        returns = self.db.collection('Stocks').document('daily').document('closes').get()
        daily_returns = returns.pct_change()
        print(daily_returns)
       
        
    #Deletes a stock from the portfolio
    #       stock = stock.upper()
    #          return True
    #        except Error:
     #           return False
           
    #Percent change in stock per day. Part of initial push to viraj branch, will add more later tonight
    #Updated by Muneeb Khan
    def percentChange(self,quantity, stockPrice, newstockPrice, day, increase, percentIncrease, AdjustClose):

        quantity = 0
        percentIncrease = 0
        AdjustClose = 0

        day = self.db.collection('Stocks').document('daily').document('dates').get() # Day will get values of dates
        stockPrice = self.db.collection('Stocks').document('daily').document('closes').get()

        if quantity > 0:
            increase = newstockPrice[day+1] - stockPrice[day]
                    
        return -1
        
        
    #Percent change in stock per day. Part of initial push to viraj branch, will add more later tonight
    #Updated by Muneeb Khan
    def percentChange(self,quantity, stockPrice, newstockPrice, day, increase, percentIncrease, AdjustClose):

        quantity = 0
        percentIncrease = 0
        AdjustClose = 0

        day = self.db.collection('Stocks').document('daily').document('dates').get() # Day will get values of dates
       #Need more inquiry
       # newstockPrice = self.db.collection('IntradayStockData').document('daily').document('closes').get()
        stockPrice = self.db.collection('Stocks').document('daily').document('closes').get()

        if quantity > 0:
            for stockPrice in day: 
                increase = newstockPrice[day+1] - stockPrice[day]
                    
            percentIncrease = (increase/stockPrice) * 100
            return percentIncrease
        else:
            return -1     
        
    #Author: Viraj Kadam    
    #Graph of user stocks   (Need buy and sell info)
    def user_graph(self, db):
        prices = self.db.collection('IntradayStockData').document('prices').get()
        dates = self.db.collection('IntradayStockData').document('dates').get
        for x in prices:
            plt.plot(x[dates][prices])
            
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.show
            
        
        
    #Display all information
    def displayInfo(self, close):
        print("Percent Change: " + self.percentChange)
        print("Returns: " + self.returns)
        print("Amount Remaining: " + self.funds_remaining)
       
        print("Profit: " + self.get_profit)
        if (self.GainorLoss > self.db.collection('IntradayStockData').document('').document('closes').get()):
            print("Gains: +" + self.GainorLoss)
        elif (self.GainorLoss < self.db.collection('Stocks').document('daily').document('closes').get()):
            print("Loss: -" + self.GainorLoss)
        
        print("Would you like to delete a stock: " + self.delete)
        print("Retrive stocks: " + self.retrieve)
        
        
        
        

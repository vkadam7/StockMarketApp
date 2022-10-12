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
investment = []
portfolio = 0
transactionCost = 0.1
amount = 1000
totalMoney = 0
port_list = []

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
    
    def retrieve(self, id):
        try:
            return self.firebase.collection("Stocks").document(id).get()
        except:
            return ''

    #Retrieves the number of shares owned by the user
    def get_shares_owned(self, db, stock, user, quantity, stockPrice):
        self.stock = stock
        data = {'name': self.name,
                'dayOfPurchase': self.dayOfPurchase,
                'quantity': self.quantity,
                'avgStockPrice': self.avgStockPrice,
                'totalPrice': self.totalPrice}
        
        self.db.collection('Stocks').document('name').get()
        
        return -1

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
        
        
        
    #Fixed this section to account for gains or losses, need to test to check if everything is correct  
    def GainorLoss(self, db, stock, quanity, stockPrice, simName=""):
        totalGain = 0
        netGain = 0
        netLoss = 0
        CurrentPrice = 0
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
                CurrentPrice = self.db.collection('Simulations').document(simName).document('Stocks').document('prices').get()
                day = self.db.collection('Stocks').document('daily').document('dates').get()
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
    def funds_remaining(self):
        intitialAmount = 1000
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
                'currentCash': self.initialCash,
                'score': 0,
                'Orders': []  
        }
        fundsUsed = intitialAmount - (tempPrice)(quantity)
        finalAmount = intitialAmount - fundsUsed

    #Edited returns feature
    def returns(self, quantity, avgStockPrice, AdjustClose):
        returns = self.db.collection('Stocks').document('daily').document('closes').get()
        daily_returns = returns.pct_change()
        print(daily_returns)
        #monthly_returns =
        
    
        
    #Deletes a stock from the portfolio
    def delete(self, stock):
            stock = stock.upper()
            try:
                self.portfolio.pop(stock)
                return True
            except Error:
                 return False
           
    #Percent change in stock per day. Part of initial push to viraj branch, will add more later tonight
    #Updated by Muneeb Khan
    def percentChange(self,quantity, stockPrice, newstockPrice, day, increase, percentIncrease, AdjustClose):

        quantity = 0
        percentIncrease = 0
        AdjustClose = 0

        day = self.db.collection('Stocks').document('daily').document('dates').get() # Day will get values of dates
        newstockPrice = self.db.collection('Stocks').document('daily').document('closes').get()
        stockPrice = self.db.collection('Stocks').document('daily').document('closes').get()

        if quantity > 0:
            for stockPrice in day: 
                increase = newstockPrice[day+1] - stockPrice[day]
                    
            percentIncrease = (increase/stockPrice) * 100
            return percentIncrease
        else:
            return -1

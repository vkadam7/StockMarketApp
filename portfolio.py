#Author: Viraj Kadam
#initial portfolio python file, will need to fix some more
from cgi import print_exception
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


db = firebase.database()
investment = []
portfolio = 0
transactionCost = 0.1
amount = 1000
totalMoney = 0
port_list = []

class portfolio:
    def __init__(self, db, stock, user, index, buyOrSell, quantity, stockPrice):
        self.db = db
        self.stock = stock
        self.user = user
        self.dayOfPurchase = index
        self.option = buyOrSell
        self.quantity = quantity
        self.avgStockPrice = stockPrice
        self.totalPrice = quantity*stockPrice
        return -1
    
    def retrieve(self, id):
        try:
            return self.firebase.child("Stocks").child(id).get().val()
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
        
        self.db.child()
        return -1

    #Need to include if statement for whether it is a net gain or loss    
    def Gain(self, db, stock, quanity, stockPrice):
        totalGain = 0
        netGainorLoss = 0
        CurrentPrice = 0
        tempData = self.db.child('Simulations').child(self.sim).child('Orders').get().val()
        data = {'name': self.name, 
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice, 
                }
        if quanity > 0:
            tempPrice = self.db.child('Stocks').child('daily').child('closes').get().val()
            CurrentPrice = self.db.child('Stocks').child('daily').child('closes').get.val()
            for CurrentPrice in i:
                netGainorLoss = (CurrentPrice[i+1] - tempPrice[i]) / (tempPrice[i]) * 100
                return netGainorLoss
        else: 
            return -1
                
                
     #Determines how much money the user has left to spend in the game. Need to include an if statement for when the user sells stocks      
    def funds_remaining(self, quantity, avgStockPrice):
        intitialAmount = 1000
        finalAmount = 0
        fundsUsed = 0
        fundsRemainiing = 0
        quantity = 0
        tempPrice = self.db.child('Stocks').child('daily').child('closes').get.val()
        data = {'name': self.name,
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice     
        }
        fundsUsed = intitialAmount - (tempPrice)(quantity)
        finalAmount = intitialAmount - fundsUsed
        
    #Deleted initial profit feature, this is going to be the new one
    def get_profit(self, db, stock, quantity, avgstockPrice):
        data = {'name' : self.name, 
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice}
        profit = 0
        


    def returns(quantity, price):
        global portfolio, amount
        allocatedMoney = quantity * price
        endResult = endResult - allocatedMoney - transactionCost * allocatedMoney
        portfolio += quantity
        if investment == []:
            investment.append(allocatedMoney)
        else:
            investment.append(allocatedMoney)
            investment[-1] += investment[-2]
        return -1
    
        
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

        day = self.db.child('Stocks').child('daily').child('dates').get().val() # Day will get values of dates
        newstockPrice = self.db.child('Stocks').child('daily').child('closes').get().val()
        stockPrice = self.db.child('Stocks').child('daily').child('closes').get().val()

        if quantity > 0:
            for stockPrice in day: 
                increase = newstockPrice[day+1] - stockPrice[day]
                    
            percentIncrease = (increase/stockPrice) * 100
            return percentIncrease
        else:
            return -1

#Author: Viraj Kadam
#initial portfolio python file, will need to fix some more
from cgi import print_exception
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
    
    
    
      #Gets Profit of the user    
##def get_profit(self, db, stock, quantity, stockPrice):
        profit = 0
        current = 0
        for price in reversed(stockPrice):
            profit = stockPrice + current
            profit = profit

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
        
        
#Deletes a stock from the portfolio
def delete(self, stock):
     stock = stock.upper()
     try:
         self.portfolio.pop(stock)
         return True
     except Error:
         return False
     
def funds_remaining():
    intitialAmount = 1000
    finalAmount = 0
    
                
            
    
    
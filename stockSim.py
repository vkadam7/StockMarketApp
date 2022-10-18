from mimetypes import init
from time import daylight
import numpy as np
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import ArrayUnion
import datetime

## doesThatStockExist
#   Description: Checks to see if that stock exists in the database yet,
#   according to the ID (ticker)
#
#   Inputs: db - Link to the database
#   ticker - stock ticker to be searched for in database
#
#   Author: Ian McNulty
def doesThatStockExist(db, searchTerm):
    tempData = db.collection('Stocks').document(searchTerm).get() 
    if tempData != None:
        return True

class StockData:
    ## StockData __init__
    #   Description: Initiates a StockData object with Database and 
    #   requested stock, for display
    #
    #   Inputs: db - Database object, connected to Firestore
    #           req - Key for requested stock
    #
    #   Author: Ian McNulty
    def __init__(self, db, req):
        self.db = db
        self.ticker = req
        self.data = self.retrieve(self.db, self.ticker)
        if self.data != 'This data entry does not exist':
            self.name = self.data['name']
            self.headquarters = self.data['headquarters']
            self.listedAt = self.data['listedAt']
            tempData = self.data['daily']
            self.dates = tempData['dates']
            self.opens = tempData['opens']
            self.highs = tempData['highs']
            self.lows = tempData['lows']
            self.closes = tempData['closes']
            self.adjCloses = tempData['adjustedCloses']
            self.volumes = tempData['volumes']
        else:
            print(self.data)

    ## StockData.getData
    #   Description: Retrieves data from start date to end date and produces
    #   a matrix for display on the webpage
    #
    #   Inputs: start - starting date for range of requested data
    #   end - ending date for range of requested data
    #
    #   Author: Ian McNulty
    def getData(self, start, end, timespan):
        try:
            dataMatrix = []
            tempArr = np.array(self.dates)
            startLoc = np.where(tempArr == start)
            endLoc = np.where(tempArr == end)
            tempOpens = []
            tempCloses = []
            tempHighs = []
            tempLows = []
            tempAdjCloses = []
            tempVolumes = []
            tempDate = start
            for i in range(startLoc[0][0], endLoc[0][0]+1):
                if timespan == 'monthly' or timespan == 'weekly':
                    if self.checkDate(i, timespan):
                        dataMatrix.append([tempDate, np.mean(tempOpens), np.mean(tempHighs),
                                        np.mean(tempLows), np.mean(tempCloses), np.mean(tempAdjCloses),
                                        np.mean(tempVolumes)])
                        tempOpens = []
                        tempCloses = []
                        tempHighs = []
                        tempLows = []
                        tempAdjCloses = []
                        tempVolumes = []
                        tempDate = self.dates[i]
                    tempOpens.append(self.opens[i])
                    tempCloses.append(self.closes[i])
                    tempHighs.append(self.highs[i])
                    tempLows.append(self.lows[i])
                    tempAdjCloses.append(self.adjCloses[i])
                    tempVolumes.append(self.volumes[i])
                elif timespan == 'hourly':
                    interp = np.interp(range(0,23),[0, 12, 23],[self.opens[i], np.mean([self.opens[i], self.closes[i]]), self.closes[i]])
                    for j in range(0,len(interp)):
                        tempArr = np.array([self.opens[i], self.closes[i], np.mean([self.opens[i], self.closes[i]])])
                        interp[j] += np.random.randn() * np.std(tempArr)
                    date = self.dates[i]
                    hourlyDates = []
                    for i in range(0,24):
                        if i < 10:
                            tempDate = date + ' 0' + str(i) + ':00:00'
                        else:
                            tempDate = date + ' ' + str(i) + ':00:00'
                        hourlyDates.append(tempDate)
                    dataMatrix.append([hourlyDates, interp])
                else:
                    dataMatrix.append([self.dates[i], self.opens[i], self.highs[i],
                                    self.lows[i], self.closes[i], self.adjCloses[i],
                                    self.volumes[i]])
            return dataMatrix
        except IndexError:
            print("One of the selected dates are unavailable")
            return -1

    ## checkDate
    #   Description: Checks the given date to see if it is the end of the selected
    #   timespan, for example, if the current day is the 31st, then it is the end 
    #   of the month or if today is the 7th and the next day in the data is more 
    #   a day away, the week must have ended
    #
    #   Inputs: index - current day in the stock being compared
    #   timespan - current timespan to check for
    #
    #   Author: Ian McNulty
    def checkDate(self, index, timespan):
        if timespan == 'monthly':
            if self.dates[index][8] == '3' and self.dates[index][9] == '1':
                return True
            elif self.dates[index][8] == '3' and self.dates[index][9] == '0':
                if self.dates[index+1][8] == '0':
                    return True
                else:
                    return False
            elif self.dates[index][8] == '2' and self.dates[index][9] == '8':
                if self.dates[index+1][8] != '2':
                    if self.dates[index+2][8] == '0':
                        return True
                else:
                    return False
            else: return False
        elif timespan == 'weekly':
            if (int(self.dates[index+1][9]) - int(self.dates[index][9])) > 1:
                return True
        else:
            return False
            
    ## stockPageFactory
    #   Description: Returns a dictionary of values to be used with the stockView
    #   HTML template
    #
    #   Author: Ian McNulty
    def stockPageFactory(self):
        stock = {
            "ticker": self.ticker,
            "name": self.name,
            "headquarters": self.headquarters,
            "listedAt": self.listedAt,
            "dates": self.dates,
            "opens": self.opens,
            "highs": self.highs,
            "lows": self.lows,
            "closes": self.closes,
            "adjCloses": self.adjCloses,
            "volumes": self.volumes
        }
        return stock

    ## StockData retrieve
    #   Description: Retrieves data from Firestore database according
    #   to requested stock ID.
    #
    #   Inputs: id - Database key for requested stock.
    #
    #   Author: Ian McNulty
    def retrieve(db, ticker, simName="", startDate="", endDate=""):
        try:
            if startDate == "":
                return db.collection("Stocks").document(ticker).get().to_dict()
            else:
                data = db.collection("Stocks").document(ticker).get().to_dict()
                dailys = data['daily']
                dates = dailys['dates']
                opens = dailys['opens']
                closes = dailys['closes']
                tempArr = np.array(dates)
                startLoc = np.where(tempArr == startDate)
                endLoc = np.where(tempArr == endDate)
                newDates = []
                newData = []
                for i in range(startLoc[0][0], endLoc[0][0]+1):
                    interp = np.interp(range(0,23),[0, 12, 23],[opens[i], np.mean([opens[i], closes[i]]), closes[i]])
                    for j in range(0,len(interp)):
                        tempArr = np.array([opens[i], closes[i], np.mean([opens[i], closes[i]])])
                        interp[j] += np.random.randn() * np.std(tempArr)
                    date = dates[i]
                    hourlyDates = []
                    for i in range(0,24):
                        if i < 10:
                            tempDate = date + ' 0' + str(i) + ':00:00'
                        else:
                            tempDate = date + ' ' + str(i) + ':00:00'
                        hourlyDates.append(tempDate)
                    for entry in hourlyDates:
                        newDates.append(entry)
                    for entry in interp.tolist():
                        newData.append(entry)
                return {
                    'simulation':simName,
                    'name': data['name'],
                    'headquarters': data['headquarters'],
                    'listedAt': data['listedAt'],
                    'dates': newDates,
                    'prices': newData,
                    'opens': opens,
                    'closes': closes,
                    'highs': dailys['highs'],
                    'lows': dailys['lows']
                }
        except KeyError:
            return 'This data entry does not exist'

    # Stock availability by Muneeb Khan
    def stockAvailability(db):
        #data = {
        #    "ticker": self.ticker,
        #    "name": self.name,
        #    "startDate": self.startDate,
        #    "endDate": self.endDate,
        #    "timespan": self.timespan
        #}
        tickers = []

        for entry in db.collection('Stocks').get():
            tickers.append(entry.id)

        return tickers
        
class Simulation:
    def __init__(self, db, user, startDate, endDate, initialCash):
        self.db = db
        self.user = user
        self.startDate = startDate
        self.endDate = endDate
        self.initialCash = initialCash
        self.stocks = []

    def createSim(self):
        count = len(self.db.collection('Simulations').get())
        simName = "Sim" + str(count+1)
        self.simName = simName
        self.startTimestamp = datetime.datetime.now()
        data = {
            'ongoing': True,
            'user': self.user,
            'startDate': self.startDate,
            'endDate': self.endDate,
            'initialCash': self.initialCash,
            'currentCash': self.initialCash,
            'score': 0,
            'startTimestamp': self.startTimestamp
        }
        self.db.collection('Simulations').document(simName).set(data)

    def whatTimeIsItRightNow(self):
        currentTime = datetime.datetime.now()
        difference = currentTime - self.startTimestamp
        index = -1
        for i in range(0,difference.days):
            index += 24
        index += (difference.seconds//3600)%24
        return index

    def currentPriceOf(self, ticker):
        data = self.db.collection('IntradayStockData').document(ticker).get()
        return data['prices'][self.whatTimeIsItRightNow()]

    def retrieveStock(self, ticker):
        stock = self.db.collection('IntradayStockData').document(ticker).get()
        return stock

    def addStocksToSim(self):
        tickerList = StockData.stockAvailability(self.db)
        for ticker in tickerList:
            tempData = StockData.retrieve(self.db, ticker, self.simName, self.startDate, self.endDate)
            self.stocks.append(tempData)
            self.db.collection('IntradayStockData').document(ticker).set(tempData)

    def updateCash(self, newAmount):
        data = self.db.collection('Simulations').document(self.simName).get()
        data['currentCash'] = newAmount
        self.db.collection('Simulations').document(self.simName).update(data)

    def finishSimulation(self):
        data = self.db.collection('Simulations').document(self.simName).get()
        data['ongoing'] = False
        percentChange = (data['currentCash'] - data['initialCash']) / data['initialCash']
        data['score'] = percentChange * 100
        self.db.collection('Simulations').document(self.sim).update(data)

    def retrieveOngoing(db, email):
        return db.collection('Simulations').where('ongoing','==',True).where('user','==',email)

class User:
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

    def retrieve(self):
        try:
            return self.db.collection('Users').document(self.username).get()
        except:
            return 'This data entry does not exist'

    def updateProfile(self, description="", picture="", experience=""):
        if description == "":
            description = self.description
        if picture == "":
            picture = self.picture
        if experience == "":
            experience = self.experience
        self.updateDescription(description)
        self.updatePicture(picture)
        self.updateExperience(experience)

    def updateDescription(self, description):
        data = self.db.collection("Users").document(self.username)
        data.update({ 'Description' : description })

    def updatePicture(self, picture):
        data = self.db.collection("Users").document(self.username)
        data.update({ 'Picture' : picture })

    def updateExperience(self, experience):
        data = self.db.collection("Users").document(self.username)
        data.update({ 'Experience' : experience })

    def registerUser(db, username, email, name, userID, description="", picture="", experience=""):
        data = {
            'Email' : email,
            'Name' : name,
            'UserID' : userID,
            'userName' : username,
            'Description' : description,
            'Picture' : picture,
            'Experience' : experience
        }
        db.collection('Users').document(username).set(data)

    # User list by Muneeb Khan
    def uesrlist(db,username, email, name, userID, description="", picture="", experience=""):
        data = {
            'Email' : email,
            'userName' : username,
            'Name' : name,
            'UserID' : userID,
            'Description' : description,
            'Picture' : picture,
            'Experience' : experience,
        }
        usernameslist = []

        tempData = db.collection('Users').document(username).get(data)
        for i in range(['Users']):
            usernameslist.append(tempData[i])
            print("\n")

        return usernameslist

class Order:
    def __init__(self, db, simulation, stock, buyOrSell, quantity, stockPrice):
        self.db = db
        self.sim = simulation
        self.stock = stock
        self.dayOfPurchase = datetime.datetime.now()
        self.option = buyOrSell
        self.quantity = quantity
        self.avgStockPrice = stockPrice
        self.totalPrice = quantity*stockPrice

    def buyOrder(self):
        if self.option == 'buy':
            count = len(self.db.collection('Simulations').document(self.sim).document('Orders').get())
            orderName = self.ticker + str(count)
            data = {
                'validity': True,
                'ticker': self.stock.ticker,
                'dayOfPurchase': self.dayOfPurchase,
                'buyOrSell': 'buy',
                'quantity': self.quantity,
                'avgStockPrice': self.avgStockPrice,
                'totalPrice': self.totalPrice
            }
            self.db.collection('Simulations').document(self.sim).document('Orders').document(orderName).set(data)
        else: return -1

    def sellOrder(self):
        if self.option == 'sell':
            tempInitialQuant = self.quantity
            tempData = self.db.collection('Simulations').document(self.sim).document('Orders').get()
            listOfChangedOrders = []
            partialOrderFlag = False
            try:
                i = 0
                while tempInitialQuant > 0:
                    orderName = self.ticker + chr(i)
                    tempOrder = tempData[orderName]
                    if tempOrder['validity'] == 'true':
                        if tempOrder['buyOrSell'] == 'buy':
                            tempCheck = tempInitialQuant - tempOrder['quantity']
                            if tempCheck < 0:
                                partialOrderFlag = True
                                finalOrderName = orderName
                                while tempCheck < 0:
                                    tempCheck += 1
                                updatedQuantity = tempCheck
                            tempInitialQuant -= tempOrder['quantity']
                            listOfChangedOrders.append(orderName)
                    i += 1
                totalPrices = []
                #stockPrices = []
                for order in listOfChangedOrders:
                    tempOrder = self.db.collection('Simulations').document(self.sim).document('Orders').document(order).get()
                    totalPrices.append(tempOrder['totalPrice'])
                    #stockPrices.append(tempOrder['avgStockPrice'])
                    updatedOrder = {
                        'validity': False,
                        'ticker': tempOrder['ticker'],
                        'dayOfPurchase': tempOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': tempOrder['quantity'],
                        'avgStockPrice': tempOrder['avgStockPrice'],
                        'totalPrice': tempOrder['totalPrice']
                    }
                    self.db.collection('Simulations').document(self.sim).document('Orders').document(order).update(updatedOrder)
                if partialOrderFlag:
                    finalOrder = self.db.collection('Simulations').document(self.sim).document('Orders').document(finalOrderName).get()
                    totalPrices.append(finalOrder['totalPrice'])
                    #stockPrices.append(finalOrder['avgStockPrice'])
                    updatedFinalOrderOriginal = {
                        'validity': False,
                        'ticker': finalOrder['ticker'],
                        'dayOfPurchase': finalOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': finalOrder['quantity'],
                        'avgStockPrice': finalOrder['avgStockPrice'],
                        'totalPrice': finalOrder['totalPrice']
                    }
                    self.db.collection('Simulations').document(self.sim).document('Orders').document(order).update(updatedFinalOrderOriginal)
                    updatedFinalOrderNew = {
                        'validity': True,
                        'ticker': finalOrder['ticker'],
                        'dayOfPurchase': finalOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': updatedQuantity,
                        'avgStockPrice': finalOrder['avgStockPrice'],
                        'totalPrice': finalOrder['totalPrice']
                    }
                    count = len(self.db.collection('Simulations').document(self.sim).document('Orders').get())
                    orderName = finalOrder['ticker'] + chr(count)
                    self.db.collection('Simulations').document(self.sim).document('Orders').document(orderName).set(updatedFinalOrderNew)
                sellOrderData = {
                    'validity': True,
                    'ticker': self.stock.ticker,
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'sell',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice
                }
                count = len(self.db.collection('Simulations').document(self.sim).document('Orders').get())
                orderName = self.ticker + chr(count)
                self.db.collection('Simulations').document(self.sim).document('Orders').document(orderName).set(sellOrderData)
                profit = sum(totalPrices) - self.totalPrice
                return profit
            except IndexError:
                return -2
        else: return -1

    # List of Orders by Muneeb Khan
    def orderlist(db, sim, stock, user, index,quantity,stockPrice):
        data = {
            'sim' : sim,
            'stock' : stock,
            'user' : user,
            'index' : index,
            'quantity' : quantity,
            'avgStockPrice' : stockPrice
        }
        orderslist = []

        tempData = db.collection('Stocks').document(stock).get(data)
        for i in range(['Stocks']):
            orderslist.append(tempData[i])
            print ("\n")

        return orderslist

        return orders
    
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
    
    def displayPortfolio(self):
        count = len(self.db.collection('Simulations').get(id))
        simName = "Sim" + str(count+1)
        self.simName = simName
        data = {
                'ongoing': True,
                'user': self.user.email,
                'startDate': self.startDate,
                'endDate': self.endDate,
                'initialCash': self.initialCash,
                'currentCash': self.initialCash,
                'score': 0,
                'Orders': [],
                'profit': 0
            }
        self.db.collection('Simulations').document(simName).set(data)
        
    
    def retrieve(self, id):
        try:
            return self.firebase.collection("Stocks").document(id).get()
        except:
            return ''

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
        return data[profit]
    
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
    def delete(self):
        try:
            stock = stock.upper()
            return True
        except Error:
            return False
           
    #Percent change in stock per day. Part of initial push to viraj branch, will add more later tonight
    #Updated by Muneeb Khan
    #def percentChange(self,quantity, stockPrice, newstockPrice, day, increase, percentIncrease, AdjustClose):

     #   quantity = 0
      #  percentIncrease = 0
       # AdjustClose = 0

#        day = self.db.collection('Stocks').document('daily').document('dates').get() # Day will get values of dates
 ##      stockPrice = self.db.collection('Stocks').document('daily').document('closes').get()

   #     if quantity > 0:
    ##           increase = newstockPrice[day+1] - stockPrice[day]
                    
      ###    return -1
        
        
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
           
    #def user_graph(self, db):
        
        
    #Display all information
    def displayInfo(self, close):
        print("Percent Change: " + self.percentChange)
        print("Returns: " + self.returns)
        print("Amount Remaining: " + self.funds_remaining)
        print("Profit: " + self.get_profit)
        if (self.GainorLoss > self.db.collection('IntraDayStockData').document('prices').get()):
            print("Gains: +" + self.GainorLoss)
            return
        elif (self.GainorLoss < self.db.collection('IntraDayStockData').document('prices').get()):
            print("Loss: -" + self.GainorLoss)
            return
        else:
            return -1
        
        print("Would you like to delete a stock: " + self.delete)
        print("Retrive stocks: " + self.retrieve)
        
        
        
        

    
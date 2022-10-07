from mimetypes import init
import numpy as np

## doesThatStockExist
#   Description: Checks to see if that stock exists in the database yet,
#   according to the ID (ticker)
#
#   Inputs: db - Link to the database
#   ticker - stock ticker to be searched for in database
#
#   Author: Ian McNulty
def doesThatStockExist(db, searchTerm):
    tempData = db.child('Stocks').child(searchTerm).get().val() 
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
        self.firebase = db
        self.ticker = req
        self.data = self.retrieve(self.ticker)
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

    ## StockData retrieve
    #   Description: Retrieves data from Firestore database according
    #   to requested stock ID.
    #
    #   Inputs: id - Database key for requested stock.
    #
    #   Author: Ian McNulty
    def retrieve(self, id):
        try:
            return self.firebase.child("Stocks").child(id).get().val()
        except:
            return 'This data entry does not exist'

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

    ## buyStock
    #   Description: Allows the given user to buy a specific stock and adds the order
    #   to the database
    #   
    #   Inputs:
    #
    #   Author: Ian McNulty
    def buyStock(self, user):
        
        return -1

    ## sellStock
    #   Description: Allows the given user to sell a specific stock and adds the order
    #   to the database
    #   
    #   Inputs:
    #
    #   Author: Ian McNulty
    def sellStock(self, user):

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

class Simulation:
    def __init__(self, db, user, startDate, endDate, initialCash):
        self.firebase = db
        self.user = user
        self.startDate = startDate
        self.endDate = endDate
        self.initialCash = initialCash

    def createSim(self):
        count = len(self.db.child('Simulations').get().val())
        simName = "Sim" + str(count)
        data = {
                'ongoing': 'true',
                'user': self.user.email,
                'startDate': self.startDate,
                'endDate': self.endDate,
                'initialCash': self.initialCash,
                'Orders': []
            }
        self.db.child('Simulations').child(simName).set(data)
        return 1

class User:
    def __init__(self):
        pass

class Order:
    def __init__(self, db, simulation, stock, user, index, buyOrSell, quantity, stockPrice):
        self.db = db
        self.sim = simulation
        self.stock = stock
        self.user = user
        self.dayOfPurchase = index
        self.option = buyOrSell
        self.quantity = quantity
        self.avgStockPrice = stockPrice
        self.totalPrice = quantity*stockPrice

    def buyOrder(self):
        if self.option == 'buy':
            count = len(self.db.child('Simulations').child(self.sim).child('Orders').get().val())
            orderName = self.ticker + str(count)
            data = {
                'validity': 'true',
                'ticker': self.stock.ticker,
                'dayOfPurchase': self.dayOfPurchase,
                'buyOrSell': 'buy',
                'quantity': self.quantity,
                'avgStockPrice': self.avgStockPrice,
                'totalPrice': self.totalPrice
            }
            self.db.child('Simulations').child(self.sim).child('Orders').child(orderName).set(data)
        else: return -1

    def sellOrder(self):
        if self.option == 'sell':
            tempInitialQuant = self.quantity
            tempData = self.db.child('Simulations').child(self.sim).child('Orders').get().val()
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
                    tempOrder = self.db.child('Simulations').child(self.sim).child('Orders').child(order).get().val()
                    totalPrices.append(tempOrder['totalPrice'])
                    #stockPrices.append(tempOrder['avgStockPrice'])
                    updatedOrder = {
                        'validity': 'false',
                        'ticker': tempOrder['ticker'],
                        'dayOfPurchase': tempOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': tempOrder['quantity'],
                        'avgStockPrice': tempOrder['avgStockPrice'],
                        'totalPrice': tempOrder['totalPrice']
                    }
                    self.db.child('Simulations').child(self.sim).child('Orders').child(order).update(updatedOrder)
                if partialOrderFlag:
                    finalOrder = self.db.child('Simulations').child(self.sim).child('Orders').child(finalOrderName).get().val()
                    totalPrices.append(finalOrder['totalPrice'])
                    #stockPrices.append(finalOrder['avgStockPrice'])
                    updatedFinalOrderOriginal = {
                        'validity': 'false',
                        'ticker': finalOrder['ticker'],
                        'dayOfPurchase': finalOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': finalOrder['quantity'],
                        'avgStockPrice': finalOrder['avgStockPrice'],
                        'totalPrice': finalOrder['totalPrice']
                    }
                    self.db.child('Simulations').child(self.sim).child('Orders').child(order).update(updatedFinalOrderOriginal)
                    updatedFinalOrderNew = {
                        'validity': 'true',
                        'ticker': finalOrder['ticker'],
                        'dayOfPurchase': finalOrder['dayOfPurchase'],
                        'buyOrSell': 'buy',
                        'quantity': updatedQuantity,
                        'avgStockPrice': finalOrder['avgStockPrice'],
                        'totalPrice': finalOrder['totalPrice']
                    }
                    count = len(self.db.child('Simulations').child(self.sim).child('Orders').get().val())
                    orderName = finalOrder['ticker'] + chr(count)
                    self.db.child('Simulations').child(self.sim).child('Orders').child(orderName).set(updatedFinalOrderNew)
                sellOrderData = {
                    'validity': 'true',
                    'ticker': self.stock.ticker,
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'sell',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice
                }
                count = len(self.db.child('Simulations').child(self.sim).child('Orders').get().val())
                orderName = self.ticker + chr(count)
                self.db.child('Simulations').child(self.sim).child('Orders').child(orderName).set(sellOrderData)
                profit = sum(totalPrices) - self.totalPrice
                return profit
            except IndexError:
                return -2
        else: return -1        
 


class portfolio:
    
    investment = []
    portfolio = 0
    transactionCost = 0.1
    amount = 1000
    totalMoney = 0
    port_list = []
    
    #Author: Viraj Kadam
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
    #Author: Viraj Kadam
    #Retrievs the stocks the user has
    def retrieve(self, id):
        try:
            return self.firebase.child("Stocks").child(id).get().val()
        except:
            return ''

    #Viraj Kadam
    #Retrieves the number of shares owned by the user
    def get_shares_owned(self, db, stock, user, quantity, stockPrice):
        self.stock = stock
        data = {'name': self.name,
                'dayOfPurchase': self.dayOfPurchase,
                'quantity': self.quantity,
                'avgStockPrice': self.avgStockPrice,
                'totalPrice': self.totalPrice}
        
        self.db.child('Stocks').child('name').get().val()
        
        return -1


    def get_profit(self, db, stock, quantity, avgstockPrice):
        profit = 0
        tempData = self.db.child('Simulations').child(self.sim).child('Orders').get().val()
        
        data = {'name' : self.name, 
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice}
        
        
        
    #Fixed this section to account for gains or losses, need to test to check if everything is correct  
    def GainorLoss(self, db, stock, quanity, stockPrice):
        totalGain = 0
        netGain = 0
        netLoss = 0
        CurrentPrice = 0
        tempData = self.db.child('Simulations').child(self.sim).child('Orders').get().val()
        data = {'name': self.name, 
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice, 
                }
        if quanity > 0:
            if totalGain > CurrentPrice:
                tempPrice = self.db.child('Stocks').child('daily').child('closes').get().val()
                CurrentPrice = self.db.child('Stocks').child('daily').child('closes').get.val()
                for CurrentPrice in i:
                    netGainorLoss = (CurrentPrice[i+1] - tempPrice[i]) / (tempPrice[i]) * 100 #Unsure if this is correct
                    if netGainorLoss > 0:
                        netLoss = "-" + netGainorLoss
                        return netLoss
                    else:
                        netGain = netGainorLoss
                        return netGain
        
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

    #Needs to be fixed
    def returns(self, quantity, avgStockPrice, ):
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
     
        
        
    #Muneeb is working on this function
   # def percentChange(quantity, stockPrice, day, percent, AdjustClose):
      #  quantity = 0
       # stockPrice = 0 
        #day = 0
        #percent = 0
        #AdjustClose = 0
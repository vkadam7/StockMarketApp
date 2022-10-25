from ast import Constant, Or
from mimetypes import init
from queue import Empty
from re import search
from statistics import mean
from this import d
from time import daylight
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import ArrayUnion
import datetime

DAYS_IN_MONTH = {
    1 : 31,
    2 : 28,
    3 : 31,
    4 : 30,
    5 : 31,
    6 : 30,
    7 : 31,
    8 : 31,
    9 : 30,
    10 : 31,
    11 : 30, 
    12 : 31
}

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
        self.data = StockData.retrieve(self.db, self.ticker)
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
            if startLoc[0].size == 0:
                print(self.ticker + " only partially available for this period, startDate")
                tempDate = start
                month = int(tempDate[5:7])
                day = int(tempDate[8:10])
                year = int(tempDate[0:4])
                while startLoc[0].size == 0:
                    day += 1
                    if day >= DAYS_IN_MONTH[month]:
                        month += 1
                        if month >= 12:
                            month = 1
                            year += 1
                        day = 1
                    if month < 10:
                        strMonth = "0" + str(month)       
                    else: 
                        strMonth = str(month)
                    if day < 10:
                        strDay = "0" + str(day)       
                    else: 
                        strDay = str(day)
                    strYear = str(year)
                    startLoc = np.where(tempArr == (strYear + "-" + strMonth + "-" + strDay))
            a = startLoc[0][0]
            if endLoc[0].size == 0:
                print(self.ticker + " only partially available for this period, startDate")
                tempDate = end
                month = int(tempDate[5:7])
                day = int(tempDate[8:10])
                year = int(tempDate[0:4])
                while endLoc[0].size == 0:
                    day -= 1
                    if day <= 0:
                        month -= 1
                        if month <= 0:
                            month = 12
                            year -= 1
                        day = DAYS_IN_MONTH[month]
                    if month < 10:
                        strMonth = "0" + str(month)       
                    else: 
                        strMonth = str(month)
                    if day < 10:
                        strDay = "0" + str(day)       
                    else: 
                        strDay = str(day)
                    strYear = str(year)
                    endLoc = np.where(tempArr == (strYear + "-" + strMonth + "-" + strDay))
            b = endLoc[0][0]
            for i in range(a, b+1):
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
                    interp = np.interp(range(0,8),[0, 4, 8],[self.opens[i], np.mean([self.opens[i], self.closes[i]]), self.closes[i]])
                    for j in range(0,len(interp)):
                        tempArr = np.array([self.opens[i], self.closes[i], np.mean([self.opens[i], self.closes[i]])])
                        interp[j] += np.random.randn() * np.std(tempArr)
                    date = self.dates[i]
                    hourlyDates = []
                    for i in range(9,17):
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
            #print("One of the selected dates are unavailable")
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
            
    ## stockJSON
    #   Description: Returns a dictionary of values to be used with the stockView
    #   HTML template
    #
    #   Author: Ian McNulty
    def stockJSON(self):
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
                #print(db.collection("Stocks").document(ticker).get().to_dict())
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
                if startLoc[0].size == 0:
                    print(ticker + " only partially available for this period, startDate")
                    tempDate = startDate
                    month = int(tempDate[5:7])
                    day = int(tempDate[8:10])
                    year = int(tempDate[0:4])
                    while startLoc[0].size == 0:
                        day += 1
                        if day >= DAYS_IN_MONTH[month]:
                            month += 1
                            if month >= 12:
                                month = 1
                                year += 1
                            day = 1
                        if month < 10:
                            strMonth = "0" + str(month)       
                        else: 
                            strMonth = str(month)
                        if day < 10:
                            strDay = "0" + str(day)       
                        else: 
                            strDay = str(day)
                        strYear = str(year)
                        startLoc = np.where(tempArr == (strYear + "-" + strMonth + "-" + strDay))
                a = startLoc[0][0]
                if endLoc[0].size == 0:
                    print(ticker + " only partially available for this period, startDate")
                    tempDate = endDate
                    month = int(tempDate[5:7])
                    day = int(tempDate[8:10])
                    year = int(tempDate[0:4])
                    while endLoc[0].size == 0:
                        day -= 1
                        if day <= 0:
                            month -= 1
                            if month <= 0:
                                month = 12
                                year -= 1
                            day = DAYS_IN_MONTH[month]
                        if month < 10:
                            strMonth = "0" + str(month)       
                        else: 
                            strMonth = str(month)
                        if day < 10:
                            strDay = "0" + str(day)       
                        else: 
                            strDay = str(day)
                        strYear = str(year)
                        endLoc = np.where(tempArr == (strYear + "-" + strMonth + "-" + strDay))
                b = endLoc[0][0]
                for i in range(a, b+1):
                    interp = np.interp(range(0,7),[0, 4, 7],[opens[i], np.mean([opens[i], closes[i]]), closes[i]])
                    for j in range(0,len(interp)):
                        tempArr = np.array([opens[i], closes[i], np.mean([opens[i], closes[i]])])
                        interp[j] += np.random.randn() * np.std(tempArr)
                    date = dates[i]
                    hourlyDates = []
                    for i in range(9,16):
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
                    'simulation': simName,
                    'name': data['name'],
                    'ticker': ticker,
                    'headquarters': data['headquarters'],
                    'listedAt': data['listedAt'],
                    'dates': newDates,
                    'prices': newData
                }
        except KeyError:
            return 'This data entry does not exist'

    # Stock availability by Muneeb Khan
    def stockList(db):
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

    ## stockSearch
    #   Description: Checks to see if that stock exists in the database yet,
    #   according to the ID (ticker)
    #
    #   Inputs: db - Link to the database
    #   ticker - stock ticker to be searched for in database
    #
    #   Author: Ian McNulty
    def stockSearch(db, searchTerm):
        tempData1 = db.collection('Stocks').document(searchTerm).get() 
        if tempData1 != None:
            return True, searchTerm

        stocksDB = db.collection('Stocks')
        for entry in stocksDB.stream():
            temp = entry.to_dict()
            ticker = temp['ticker'].lower()
            name = temp['name'].lower()
            tempSearchTerm = searchTerm.lower()
            if tempSearchTerm == ticker:
                return True, ticker.upper()
            if tempSearchTerm in name:
                return True, ticker.upper()

        return False, -1
        
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
            'startTimestamp': self.startTimestamp,
        }
        self.addStocksToSim()
        self.db.collection('Simulations').document(simName).set(data)

    def whatTimeIsItRightNow(self):
        currentTime = datetime.datetime.now()
        difference = currentTime - self.startTimestamp
        index = -1
        for i in range(0,difference.days):
            index += 8
        index += (difference.seconds//3600)%24
        return index

    def currentPriceOf(self, ticker):
        data = self.db.collection('IntradayStockData').where('simulation','==',self.simName).where('ticker','==',ticker).get()
        for entry in data:
            fin = entry.to_dict()
            print(fin['prices'][self.whatTimeIsItRightNow()])
        return fin['prices'][self.whatTimeIsItRightNow()]

    def retrieveStock(self, ticker):
        stock = self.db.collection('IntradayStockData').where('simulation','==',self.simName).where('ticker','==',ticker).get()
        return stock

    def addStocksToSim(self):
        tickerList = StockData.stockList(self.db)
        for ticker in tickerList:
            tempData = StockData.retrieve(self.db, ticker, self.simName, self.startDate, self.endDate)
            self.stocks.append(tempData)
            self.db.collection('IntradayStockData').add(tempData)

    def finishSimulation(db, simName):
        data = db.collection('Simulations').document(simName).get().to_dict()
        data['ongoing'] = False
        percentChange = (float(data['currentCash']) - float(data['initialCash'])) / float(data['initialCash'])
        data['score'] = percentChange * 100
        db.collection('Simulations').document(simName).update(data)

    def retrieveOngoing(db, email):
        for query in db.collection('Simulations').where('ongoing','==',True).where('user','==',email).stream():
            id = query.id
            entry = query.to_dict()

        tempSim = Simulation(db, email, entry['startDate'], entry['endDate'], entry['initialCash'])
        tempSim.simName = id
        tempSim.startTimestamp = datetime.datetime.fromtimestamp(entry['startTimestamp'].timestamp())
        tempSim.currentCash = round(float(entry['currentCash']), 2)
        tempSim.initialCash = entry['initialCash']
        tempSim.stocks = []
        for entry in db.collection('IntradayStockData').where('simulation','==',id).stream():
            temp = entry.to_dict()
            tempSim.stocks.append(temp)

        return tempSim
    
    def updateCash(db, sim, delta):
        data = db.collection('Simulations').document(sim).get().to_dict()
        currentCash = data['currentCash']
        newCurrentCash = float(currentCash) + float(delta)
        db.collection('Simulations').document(sim).update({'currentCash' : newCurrentCash})

    def retrieveCurrentCash(db, sim):
        data = db.collection('Simulations').document(sim).get().to_dict()
        return data['currentCash']

class SimulationFactory:
    def __init__(self, db, email):
        self.simulation = Simulation.retrieveOngoing(db, email)

    def existenceCheck(db, email):
        array = [entry for entry in db.collection('Simulations').where('ongoing','==',True).where('user','==',email).stream()]
        if len(array) == 0:
            return False
        else:
            return True

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
    def userList(db):
        #data = {
        #     'Email' : self.email,
        #     'userName' : self.username,
        #     'Name' : self.name,
        #     'UserID' : self.userID,
        #}

        # The usernames list function will loop through the usernames in firebase and store each one
        # under the usernameslist [] array. - Muneeb Khan
        usernameslist = [] # Set userlist 

        for entry in db.collection('Users').stream(): # To loop through usernames in firebase
            temp = entry.to_dict()
            usernameslist.append([temp['userName']])

        df = pd.DataFrame(usernameslist, columns=['userName'])
        print(df)
        return df                       

class Order:
    def __init__(self, db, simulation, stock, buyOrSell, quantity, stockPrice):
        self.db = db
        self.sim = simulation
        self.stock = stock
        self.dayOfPurchase = datetime.datetime.now()
        self.option = buyOrSell
        self.quantity = quantity
        self.avgStockPrice = stockPrice
        self.totalPrice = float(quantity)*stockPrice

    def buyOrder(self):
        if self.option == 'Buy':
            if self.doTheyHaveEnoughMoney():
                count = len(self.db.collection('Orders').where('simulation', '==', self.sim).get())
                orderName = self.sim + self.stock['ticker'] + str(count)
                data = {
                    'sold': False,
                    'simulation': self.sim,
                    'ticker': self.stock['ticker'],
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'Buy',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice
                }
                self.db.collection('Orders').document(orderName).set(data)
                Simulation.updateCash(self.db, self.sim, float(self.totalPrice) * -1)
                return 1
            else: return -1

    def sellOrder(self):
        if self.option == 'Sell':
            if self.doTheyOwnThat() == True:
                count = len(self.db.collection('Orders').where('simulation', '==', self.sim).get())
                orderName = self.sim + self.stock['ticker'] + str(count)
                data = {
                    'simulation': self.sim,
                    'ticker': self.stock['ticker'],
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'Sell',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice
                }
                self.db.collection('Orders').document(orderName).set(data)
                Simulation.updateCash(self.db, self.sim, self.totalPrice)
                return 1
            else: return -1

    def doTheyHaveEnoughMoney(self):
        enoughFlag = False

        currentCash = int(self.db.collection('Simulations').document(self.sim).get().to_dict()['currentCash'])
        if currentCash >= self.totalPrice:
            enoughFlag = True

        return enoughFlag

    def doTheyOwnThat(self):
        quantityOwned = 0
        ownageFlag = False
        partialFlag = False
        for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock['ticker']).get():
            temp = entry.to_dict()
            if temp.get('newQuantity') != None:
                quantityOwned += int(temp['newQuantity'])
                partialFlag = True
            else:
                quantityOwned += int(temp['quantity'])

        print(quantityOwned)
        if quantityOwned >= int(self.quantity):
            ownageFlag = True
        
        amountToSell = int(self.quantity)
        if ownageFlag:
            while amountToSell > 0:
                if partialFlag == True:
                    for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock['ticker']).where('partiallySold','==',True).stream():
                        temp = entry.to_dict()
                        print("Difference is: " + str(amountToSell) + "-" + str(temp['newQuantity']) + "=" + str(amountToSell - int(temp['newQuantity'])))
                        if amountToSell - int(temp['newQuantity']) >= 0:
                            self.db.collection('Orders').document(entry.id).update({'sold' : True, 'newQuantity' : 0})
                            amountToSell -= int(temp['newQuantity'])
                        else:
                            self.db.collection('Orders').document(entry.id).update({'partiallySold' : True, 'newQuantity' : abs(int(temp['newQuantity']) - amountToSell)})
                            amountToSell -= abs(int(temp['newQuantity']) - amountToSell)
                for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock['ticker']).stream():
                    temp = entry.to_dict()
                    print("Difference is: " + str(amountToSell) + "-" + temp['quantity'] + "=" + str(amountToSell - int(temp['quantity'])))
                    if amountToSell - int(temp['quantity']) >= 0:
                        self.db.collection('Orders').document(entry.id).update({'sold' : True})
                        amountToSell -= int(temp['quantity'])
                    else:
                        self.db.collection('Orders').document(entry.id).update({'partiallySold' : True, 'newQuantity' : abs(int(temp['quantity']) - amountToSell)})
                        amountToSell -= abs(int(temp['quantity']) - amountToSell)

            return ownageFlag
        
        return ownageFlag

    def retrieve(db, sim, ticker):
        return db.collection('Orders').where('simulation','==',sim).where('ticker','==',ticker).stream()

    def retrieveOwned(db, sim, ticker):
        return db.collection('Orders').where('simulation','==',sim).where('ticker','==',ticker).where('sold','==',False).stream()

    def stocksBought(db, sim):
        tickers = []
        for entry in db.collection('Orders').where('simulation','==',sim).stream():
            temp = entry.to_dict()
            tickers.append(temp['ticker'])
        print(tickers)
        return [*set(tickers)]

    # List of Orders by Muneeb Khan
    def orderList(db):
        quantityOwned = 0
        ownageFlag = True
        # data = {
        #         'simulation': self.sim,
        #         'ticker': self.stock['ticker'],
        #         'dayOfPurchase': self.dayOfPurchase,
        #         'buyOrSell': self.buyOrSell,
        #         'quantity': self.quantity,
        #         'avgStockPrice': self.avgStockPrice,
        #         'totalPrice': self.totalPrice
        #     }

        # The order list function will loop through the orders in firebase and store each one
        # under the ordernameslist [] array. - Muneeb Khan
        orderslist = []

        for entry in db.collection('IntradayStockData').stream(): # To loop through the users orders
            temp = entry.to_dict()
            orders = temp['prices']
            orderslist.append(temp)

        return orderslist

        return orders
    
class portfolio:
    def __init__(self, db, stock, user, simulation, initialCash):
            self.firebase = db
            self.stock = stock
            self.user = user
            self.initialCash = initialCash
            self.sim = simulation 
            #self.fundsRemaining = fundsRemaining
            #self.dayofPurchase = datetime.datetime.now()
            self.currentCash = Simulation.retrieveCurrentCash(db, simulation)
            self.quantity = self.weight()
            self.profit = self.get_profit()
    
    #def retrieve(self, id):
    #    stockRetrieved = self.db.collection('Simulations').document(simName).document('intradayStockDataTableKey').get()
    #    return stockRetrieved

    #round(SimulationFactory(dbfire, session['user']).simulation.currentPriceOf(stock['ticker']), 2)
    #Returns profit from the simulator(Need to test and fix if needed )
    def get_profit(self):
        currentPriceOfStock = round(SimulationFactory(self.firebase, self.user).simulation.currentPriceOf(self.stock), 2)
        prices = []
        amountOfSharesOwned = 0
        for entry in Order.retrieve(self.firebase, self.sim, self.stock):
            temp = entry.to_dict()
            prices.append(float(temp['totalPrice']))
            if temp.get('newQuantity') != None:
                amountOfSharesOwned += int(temp['newQuantity'])
            else:
                amountOfSharesOwned += int(temp['quantity'])
        avgPriceOfOrders = mean(prices)
        currentValueOfShares = currentPriceOfStock * amountOfSharesOwned
        return round(currentValueOfShares - avgPriceOfOrders, 2)

        #profit = 0
        #quantity = self.db.collection('Orders').document('quantity').get()
        #if Order.buyOrder() == True:
        #    tempPrice = self.db.collection('Order').document('avgStockPrice').get()
        #    quantity = self.db.collection('Orders').document('quantity').get()
        #    profit += tempPrice * quantity
        #    return profit
        #elif Order.sellOrder() == True:
        #    tempPrice = self.db.collection('Order').document('avgStockPrice').get()
        #    quantity = self.db.collection('Orders').document('quantity').get()
        #    profit -= tempPrice * quantity
        #    return profit
            
    #Displays amount of shares owned (To also be implemented later)
    def weight(self):
        quantity = 0
        for entry in Order.retrieveOwned(self.firebase, self.sim, self.stock):
            temp = entry.to_dict()
            if temp.get('newQuantity') != None:
                quantity += int(temp['newQuantity'])
            else:
                quantity += int(temp['quantity'])
        return quantity

        #share = [self.quantity]
        #max_share = 1
        #for share in max_share:
        #    if(self.quantity <= max_share and self.quantity >= 0):
        #        return share[self.quantity]
        #    else:
        #        return -1   
        

    #
    #
    #
    #
    # I dont think this is necessary - Ian
    #               |
    #               |
    #               |
    #               V
    #Fixed this section to account for gains or losses, need to test to check if everything is correct  
    def GainorLoss(self, db, stock, quanity, stockPrice, simName=""):
          #tempData = self.db.collection('Simulations').document(self.sim).document('Orders').get()
        data = {'name': self.name, 
                'quantity': self.quantity, 
                'avgStockPrice': self.avgStockPrice, 
                }
        currentCash = self.db.collection('Simulations').document(self.sim).document('currentCash').get()
        currentPrice = Simulation.currentPriceOf
        day = datetime()
        
        
        stocksOwned = self.db.collection('Orders').document(self.sim).document('ticker')

        if quanity > 0:    
            if currentCash > currentPrice:
                tempPrice = self.db.collection('Simulations').document(simName).document('Stocks').document('prices').get()
                #Need to fix this function
                #CurrentPrice = self.db.collection('Stocks').document('daily').document('closes').get
                
                netLoss = "-" + netGainorLoss
                print("Net loss" + netLoss )
                return netLoss
            else:
                netGain = netGainorLoss
                print("Net Gain: " + netGain)
                return netGain
        if Order.buyOrder == True:
                netGainorLoss = (currentPrice[day + 1] - tempPrice[day]) / (tempPrice[day]) * 100
                return netGainorLoss
        elif Order.sellOrder == True:
                 netGainorLoss = (currentPrice[day + 1] - tempPrice[day]) / (tempPrice[day]) * 100
                 return netGainorLoss

      
    #
    #
    #
    #
    # Calculated by: self.currentCash = Simulation.retrieveCurrentCash(db, simulation)
    #               |
    #               |
    #               |
    #               V                     
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
                'currentCash': self.currentCash,
                'score': 0,
                'Orders': []  
        }

        if Order.buyOrder() == True:
            if data ['currentCash'] == data['initialCash']:
                return data['currentCash']
            elif data['currentCash'] > data['initialCash']:
                 fundsUsed = data['currentCash'] - data['initialCash']
                 fundsRemainiing = fundsUsed
                 return fundsRemainiing
        elif Order.sellOrder():
            if data ['currentCash'] == data['initialCash']:
                return data['currentCash']
            elif data['currentCash'] > data['initialCash']:
                 fundsUsed = data['currentCash'] - data['initialCash']
                 fundsRemainiing = fundsUsed
                 return fundsRemainiing
       
        
    #Edited returns feature
    def returns(self, quantity, avgStockPrice, AdjustClose):
        returns = self.db.collection('Stocks').document('daily').document('closes').get()
        daily_returns = returns.pct_change()
        print(daily_returns)
       
           
    #Percent change in stock per day. Part of initial push to viraj branch, will add more later tonight
    #Updated by Muneeb Khan
    def percentChange(self,quantity, stockPrice, newstockPrice, day, increase, percentIncrease, AdjustClose):

        
        percentIncrease = 0
        AdjustClose = 0

        day = self.db.collection('Stocks').document('daily').document('dates').get() # Day will get values of dates
       #Need more inquiry
       # newstockPrice = self.db.collection('IntradayStockData').document('daily').document('closes').get()
        stockPrice = self.db.collection('Stocks').document('daily').document('closes').get()
        stock=  self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock['ticker']).stream()
        quantity = self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('quantity', '==', self.stock['quantity']).stream()
        for i in stock:
             if quantity > 0:
                for stockPrice in day: 
                    increase = newstockPrice[day+1] - stockPrice[day]
                percentIncrease = (increase/stockPrice) * 100
                return percentIncrease
        else:
            return -1     
        
    #Author: Viraj Kadam    
    #Graph of user stocks   (Need buy and sell info)
    #def user_graph(self, db):
    #   prices = self.db.collection('IntradayStockData').document('prices').get()
    #    dates = self.db.collection('IntradayStockData').document('dates').get()
    #    for x in prices:
    #        plt.plot(x[dates][prices])
    #        
    #    plt.xlabel('Date')
    #    plt.ylabel('Price')
    #    plt.show
            
        
        
    #Display all information
    def displayInfo(self, close):
        print(self.percentChange)
        print(self.returns)
        print(self.funds_remaining)

        print(self.get_profit)
        if (self.GainorLoss > self.db.collection('IntradayStockData').document('').document('closes').get()):
            print("Gains: +" + self.GainorLoss)
        elif (self.GainorLoss < self.db.collection('Stocks').document('daily').document('closes').get()):
            return
from mimetypes import init
from queue import Empty
from time import daylight
import numpy as np
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import ArrayUnion
import datetime


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
            if not startLoc:
                startLoc[0][0] = 0
                print(self.ticker + " only partially available for this period")
            if not endLoc:
                endLoc[0][0] = len(self.dates) - 1
                print(self.ticker + " only partially available for this period")
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
                print(ticker)
                print(startLoc)
                print(endLoc)
                if startLoc[0].size == 0:
                    a = 0
                    print(ticker + " only partially available for this period, startDate")
                else:
                    a = startLoc[0][0]
                if endLoc[0].size == 0:
                    b = len(dates) - 1
                    print(ticker + " only partially available for this period, endDate")
                else:
                    b = endLoc[0][0]
                for i in range(a, b+1):
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
        tempData = db.collection('Stocks').document(searchTerm).get() 
        if tempData != None:
            return True
        
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
        for i in range(0,difference.days+1):
            index += 24
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

    def finishSimulation(self):
        data = self.db.collection('Simulations').document(self.simName).get().to_dict()
        data['ongoing'] = False
        percentChange = (float(data['currentCash']) - float(data['initialCash'])) / float(data['initialCash'])
        data['score'] = percentChange * 100
        self.db.collection('Simulations').document(self.simName).update(data)

    def retrieveOngoing(db, email):
        for query in db.collection('Simulations').where('ongoing','==',True).where('user','==',email).stream():
            id = query.id
            entry = query.to_dict()

        tempSim = Simulation(db, email, entry['startDate'], entry['endDate'], entry['initialCash'])
        tempSim.simName = id
        tempSim.startTimestamp = datetime.datetime.fromtimestamp(entry['startTimestamp'].timestamp())
        tempSim.currentCash = entry['currentCash']
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
    def userList(self):
        data = {
            'Email' : self.email,
            'userName' : self.username,
            'Name' : self.name,
            'UserID' : self.userID,
        }

        usernameslist = []

        for entry in self.db.collection('Users').document(self.username).get(data):
            usernameslist.append(entry.id)

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
        self.totalPrice = float(quantity)*stockPrice

    def buyOrder(self):
        if self.option == 'Buy':
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
        else: return -1

    def sellOrder(self):
        if self.option == 'Sell':
            if self.doTheyOwnThat():
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
        else: return -1

    def doTheyOwnThat(self):
        quantityOwned = 0
        ownageFlag = False
        for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock['ticker']).get():
            temp = entry.to_dict()
            quantityOwned += int(temp['quantity'])

        if quantityOwned <= int(self.quantity):
            ownageFlag = True
        
        if ownageFlag:
            for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock['ticker']).where('partiallySold','==',True).stream():
                temp = entry.to_dict()
                if quantityOwned - int(temp['newQuantity']) >= 0:
                    self.db.collection('Orders').document(entry.id).update({'sold' : True})
                    quantityOwned -= int(temp['newQuantity'])
                else:
                    self.db.collection('Orders').document(entry.id).update({'partiallySold' : True, 'newQuantity' : abs(int(temp['newQuantity']) - quantityOwned)})
            for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock['ticker']).stream():
                temp = entry.to_dict()
                if quantityOwned - int(temp['quantity']) >= 0:
                    self.db.collection('Orders').document(entry.id).update({'sold' : True})
                    quantityOwned -= int(temp['quantity'])
                else:
                    self.db.collection('Orders').document(entry.id).update({'partiallySold' : True, 'newQuantity' : abs(int(temp['quantity']) - quantityOwned)})
            return ownageFlag
        
        return ownageFlag

    # List of Orders by Muneeb Khan
    def orderList(self):
        data = {
            'validity': True,
            'ticker': self.stock.ticker,
            'dayOfPurchase': self.dayOfPurchase,
            'buyOrSell': self.buyOrSell,
            'quantity': self.quantity,
            'avgStockPrice': self.avgStockPrice,
            'totalPrice': self.totalPrice
            }
        orderslist = []

        for entry in self.db.collection('Simulations').document(self.sim).document('Orders').get(data):
            orderslist.append(entry.id)

        return orderslist

        return orders
    
    
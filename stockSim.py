from ast import Constant, Or
from mimetypes import init
from queue import Empty
from re import search
from statistics import mean, quantiles
from this import d
from time import daylight
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import ArrayUnion
import datetime

import math





#import matplotlib as plt
#import matplotlib.animation as animation
#import matplotlib.pyplot as plt
#from matplotlib import style
#import math
#import mpld3
#from mpld3 import plugins



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
                    for j in range(9,17):
                        if timespan == '10minute':
                            for k in range(0,5):
                                if i < 10:
                                    tempDate = date + ' 0' + str(j) + ':' + str(k) + '0' + ':00'
                                else:
                                    tempDate = date + ' ' + str(j) + ':' + str(k) + '0' + ':00'
                        else:
                            if i < 10:
                                tempDate = date + ' 0' + str(j) + ':00:00'
                            else:
                                tempDate = date + ' ' + str(j) + ':00:00'
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
            ## General Retrieve data
            if startDate == "":
                return db.collection("Stocks").document(ticker).get().to_dict()
            
            ## Specialized retrieve data for IntradayStockData creation
            else:
                data = db.collection("Stocks").document(ticker).get().to_dict()
                dailys = data['daily']
                dates = dailys['dates']
                opens = dailys['opens']
                closes = dailys['closes']
                tempArr = np.array(dates)
                initialDate = tempArr[0]
                finalDate = tempArr[len(tempArr)-1]
                print(initialDate)
                print(endDate)
                availabilityFlag = True

                ## Checks if the stock is available for this timespan
                if int(initialDate[0:4]) > int(endDate[0:4]):
                    availabilityFlag = False
                if int(initialDate[0:4]) == int(endDate[0:4]):
                    if int(initialDate[5:7]) > int(endDate[5:7]):
                        availabilityFlag = False
                    elif int(initialDate[5:7]) == int(endDate[5:7]):
                        if int(initialDate[8:10]) > int(endDate[8:10]):
                            availabilityFlag = False

                print(availabilityFlag)
                ## If the stock is unavailable, code creates an empty entry with a
                ##  true value in the unavailable field
                if availabilityFlag == False:
                    return {
                        'simulation': simName,
                        'name': data['name'],
                        'ticker': ticker,
                        'headquarters': data['headquarters'],
                        'listedAt': data['listedAt'],
                        'unavailable': True
                    }

                ## If the stock is available, the data is processed to create a 
                ##  corresponding entry in the IntradayStockData Firestore db
                else:
                    startLoc = np.where(tempArr == startDate)
                    endLoc = np.where(tempArr == endDate)
                    newDates = []
                    newData = []

                    ## Start Date Calculation algorithm
                    if startLoc[0].size == 0:
                        print(ticker + " only partially available for this period, startDate")
                        tempDate = startDate
                        month = int(tempDate[5:7])
                        day = int(tempDate[8:10])
                        year = int(tempDate[0:4])
                        initialYear = int(initialDate[0:4])
                        if initialYear <= year:
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
                        else:
                            startLoc = np.where(tempArr == initialDate)
                    a = startLoc[0][0]

                    ## End Date Calculation algorithm
                    if endLoc[0].size == 0:
                        print(ticker + " only partially available for this period, startDate")
                        tempDate = endDate
                        month = int(tempDate[5:7])
                        day = int(tempDate[8:10])
                        year = int(tempDate[0:4])
                        finalYear = int(finalDate[0:4])
                        if finalYear >= year:
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
                        else:
                            endLoc = np.where(tempArr == finalDate)
                    b = endLoc[0][0]

                    ## Data interpolation
                    for i in range(a, b+1):
                        interpHourly = np.interp(range(0,8),[0, 4, 8],[opens[i], np.mean([opens[i], closes[i]]), closes[i]])
                        interps = []
                        interpHourly[0] += np.random.randn() * np.std(np.array([opens[i], closes[i], np.mean([opens[i], closes[i]])]))
                        for j in range(1,len(interpHourly)):
                            tempArr = np.array([opens[i], closes[i], np.mean([opens[i], closes[i]])])
                            interpHourly[j] += np.random.randn() * np.std(tempArr)
                            temp = interpHourly[j]
                            temp += np.random.randn()/10 * np.std(tempArr)
                            tempInterp = np.interp(range(6), [0, 5], [interpHourly[j-1], temp])
                            for element in tempInterp:
                                element += + np.random.randn() * np.std(tempArr)
                            interps.append(tempInterp)

                        ## Date calculations
                        date = dates[i]
                        dateEntries = []
                        for j in range(3,6):
                            tempDate = date + ' 09:' + str(j) + '0:00'
                            dateEntries.append(tempDate)
                        for j in range(10,16):
                            for k in range(0,6):
                                tempDate = date + ' ' + str(j) + ':' + str(k) + '0:00'
                                dateEntries.append(tempDate)
                        dateEntries.append(date + ' 16:00:00')

                        ## Array creations
                        for entry in dateEntries:
                            newDates.append(entry)
                        for entry in interps:
                            for point in entry.tolist():
                                newData.append(point)
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
    def stockSearch(db, searchTerm, simName):

        stocksDB = db.collection('IntradayStockData').where('simulation','==',simName)
        for entry in stocksDB.stream():
            temp = entry.to_dict()
            if temp['ticker'] == searchTerm:
                if temp.get('unavailable') != None:
                    return False, -1
                else:
                    return True, searchTerm.upper()

        for entry in stocksDB.stream():
            temp = entry.to_dict()
            ticker = temp['ticker'].lower()
            tempSearchTerm = searchTerm.lower()
            if tempSearchTerm == ticker:
                if temp.get('unavailable') != None:
                    return False, -1
                else:
                    return True, ticker.upper()

        for entry in stocksDB.stream():
            temp = entry.to_dict()
            ticker = temp['ticker'].lower()
            name = temp['name'].lower()
            tempSearchTerm = searchTerm.lower()
            print(tempSearchTerm)
            print(name)
            if tempSearchTerm in name:
                if temp.get('unavailable') != None:
                    return False, -1
                else:
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
        updateTime, tempRef = self.db.collection('Simulations').add(data)
        self.simName = tempRef.id
        self.addStocksToSim()

    def whatTimeIsItRightNow(self):
        currentTime = datetime.datetime.now()
        difference = currentTime - self.startTimestamp
        index = -1
        total = difference.total_seconds()
        days = round(total//86400)
        total -= days*86400
        hours = round(total//3600)
        total -= hours*3600
        tenMin = round(total//600)
        for i in range(0,days):
            index += 40
        for i in range(0,hours):
            index += 6
        index += tenMin
        return index

    def currentPriceOf(self, ticker):
        data = self.db.collection('IntradayStockData').where('simulation','==',self.simName).where('ticker','==',ticker).get()
        for entry in data:
            fin = entry.to_dict()
            highestIndex = Simulation.maxIndex(self.db, self.simName)
            if highestIndex > self.whatTimeIsItRightNow():
                return fin['prices'][self.whatTimeIsItRightNow()]
            return fin['prices'][len(fin['prices'])-1]

    def retrieveStock(self, ticker):
        stock = self.db.collection('IntradayStockData').where('simulation','==',self.simName).where('ticker','==',ticker).get()
        return stock

    def addStocksToSim(self):
        tickerList = StockData.stockList(self.db)
        for ticker in tickerList:
            tempData = StockData.retrieve(self.db, ticker, self.simName, self.startDate, self.endDate)
            self.stocks.append(tempData)
            self.db.collection('IntradayStockData').add(tempData)

    def amountOwned(self, ticker):
        quantityOwned = 0
        for entry in Order.retrieve(self.db, self.simName, ticker):
            temp = entry.to_dict()
            if temp.get('newQuantity') != None:
                if temp.get('sold') != None:
                    if temp['sold'] == False:
                        quantityOwned += int(temp['newQuantity'])
            else:
                if temp.get('sold') != None:
                    if temp['sold'] == False:
                        quantityOwned += int(temp['quantity'])   
        return quantityOwned

    def finishSimulation(db, simName):
        data = db.collection('Simulations').document(simName).get().to_dict()

        quantities = []
        currentPrices = []
        totalValue = 0
        
        for entry in Order.stocksBought(db, simName):
            Portfolio = portfolio(db, entry, data['user'], simName)
            if Portfolio.quantity != 0:
                quantities.append(Portfolio.quantity)
                currentPrices.append(round(SimulationFactory(db, data['user']).simulation.currentPriceOf(entry), 2))
        
        for i in range(len(quantities)):
            totalValue += quantities[i] * currentPrices[i]

        percentChange = ((float(data['currentCash']) + totalValue) - float(data['initialCash'])) / float(data['initialCash'])
        scores = percentChange * 100
        scoreRounded = round(scores)
        grabDataEmail = data['user']
        userEmail = db.collection('Users').where('Email', '==', grabDataEmail)
        for docs in userEmail.stream():
                emails = docs.to_dict()
        grabUserName = emails['userName']

        db.collection('Leaderboard').add({"email":grabDataEmail, "score":scoreRounded, "username":grabUserName})

        for entry in db.collection('IntradayStockData').where('simulation','==',simName).stream():
            temp = entry.id
            db.collection('IntradayStockData').document(temp).delete()

        data['score'] = percentChange * 100
        data['ongoing'] = False
        db.collection('Simulations').document(simName).update(data)

    def checkDates(startDate, endDate):
        if int(startDate[0:4]) >= int(endDate[0:4]):
            if int(startDate[5:7]) > int(endDate[5:7]):
                return False
            elif int(startDate[5:7]) == int(endDate[5:7]):
                if int(startDate[8:10]) >= int(endDate[8:10]):
                    return False
        return True

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

    def maxIndex(db, sim):
        highestIndex = 0
        for entry in db.collection('IntradayStockData').where('simulation','==',sim).stream():
            temp = entry.to_dict()
            if temp.get('unavailable') == None:
                if len(temp['prices']) > highestIndex:
                    highestIndex = len(temp['prices'])
        return highestIndex

    def ongoingCheck(db, sim, email):
        index = SimulationFactory(db, email).simulation.whatTimeIsItRightNow()        
        highestIndex = Simulation.maxIndex(db,sim)
        if index > highestIndex:
            return False
        return True

    def listSims(db, user):
        sims = []
        dates = []
        scores = []
        links = []
        #button = []
        i = 1
        for entry in db.collection('Simulations').where('user','==',user).where('ongoing','==',False).stream():
            temp = entry.to_dict()
            sims.append(str(i))
            date = str(datetime.datetime.fromtimestamp(temp['startTimestamp'].timestamp()).strftime("%Y-%m-%d %H:%M:%S"))
            dates.append(date)
            scores.append("%.2f" % round(float(temp['score']), 2))
            link = str('/orderHist/'+entry.id)
            links.append(link)
            i+=1
        return sims, dates, scores, links

    def completedCheck(db, user):
        count = 0
        for query in db.collection('Simulations').where('ongoing','==',False).where('user','==',user).stream():
            count += 1
        if count >= 1:
            return True
        return False

    def getPortfolioValue(db, simName):
        quantities = []
        currentPrices = []
        totalValue = 0
        data = db.collection('Simulations').document(simName).get().to_dict()
        
        for entry in Order.stocksBought(db, simName):
            Portfolio = portfolio(db, entry, data['user'], simName)
            if Portfolio.quantity != 0:
                quantities.append(Portfolio.quantity)
                currentPrices.append(round(SimulationFactory(db, data['user']).simulation.currentPriceOf(entry), 2))
        
        for i in range(len(quantities)):
            totalValue += quantities[i] * currentPrices[i]

        return totalValue, data['currentCash']

    def getAvailableStockList(db, simName, email):
        index = SimulationFactory(db, email).simulation.whatTimeIsItRightNow()        
        tickers = []
        prices = []
        links = []
        names = []
        for entry in db.collection('IntradayStockData').where('simulation','==',simName).stream():
            temp = entry.to_dict()
            if temp.get('unavailable') == None:
                if len(temp['prices']) > index:
                    tickers.append(str(temp['ticker']))
                    prices.append("%.2f" % round(temp['prices'][index],2))
                    links.append(str('/displayStock?ticker='+temp['ticker']+'&timespan=hourly'))
                    names.append(str(temp['name']))
        return tickers, prices, links, names

class SimulationFactory:
    def __init__(self, db, email):
        self.simulation = Simulation.retrieveOngoing(db, email)

    def existenceCheck(db, email):
        array = [entry for entry in db.collection('Simulations').where('ongoing','==',True).where('user','==',email).stream()]
        if len(array) == 0:
            return False, "None"
        else:
            return True, array[0].id

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

    #No longer part of follower feature
    #def addFriend(db, user1, user2):
    #    data = {
    #        'user1': user1,
    #        'user2': user2
    #    }
    #    db.collection("Users").add(data)

    #def removeFriend(db, user1, user2):
    #    for entry in db.collection('Users').where('user1','==',user1).where('user2','==',user2).stream():
    #        db.collection('Users').document(entry.id).delete()

    def listFriends(db, user):
        friends = []
        for entry in db.collection('Users').where('user1','==',user).stream():
            temp = entry.to_dict()
            friends.append(temp['user2'])
        return friends

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
        self.totalPrice = float(quantity)*float(stockPrice)

    def buyOrder(self):
        if self.option == 'Buy':
            if self.doTheyHaveEnoughMoney():
                count = len(self.db.collection('Orders').where('simulation', '==', self.sim).get())
                orderName = self.sim + self.stock + str(count)
                data = {
                    'sold': False,
                    'simulation': self.sim,
                    'ticker': self.stock,
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
            check, averagePrice = self.doTheyOwnThat()
            if check == True:
                count = len(self.db.collection('Orders').where('simulation', '==', self.sim).get())
                orderName = self.sim + self.stock + str(count)
                data = {
                    'simulation': self.sim,
                    'ticker': self.stock,
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'Sell',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice,
                    'profit': float(self.avgStockPrice)*float(self.quantity) - float(averagePrice)*float(self.quantity)
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
        for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock).get():
            temp = entry.to_dict()
            if temp.get('newQuantity') != None:
                quantityOwned += int(temp['newQuantity'])
                partialFlag = True
            else:
                quantityOwned += int(temp['quantity'])

        if quantityOwned >= int(self.quantity):
            ownageFlag = True
        
        averagePrice = []
        amountToSell = int(self.quantity)
        if ownageFlag:
            while amountToSell > 0:
                if partialFlag == True:
                    for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock).where('partiallySold','==',True).stream():
                        if amountToSell <= 0:
                            break
                        temp = entry.to_dict()
                        averagePrice.append(float(temp['avgStockPrice']))
                        if int(temp['newQuantity']) - amountToSell > 0:
                            self.db.collection('Orders').document(entry.id).update({'partiallySold' : True, 'newQuantity' : abs(int(temp['newQuantity']) - amountToSell)})
                            amountToSell -= abs(int(temp['newQuantity']) - amountToSell)
                        else:
                            self.db.collection('Orders').document(entry.id).update({'sold' : True, 'newQuantity' : 0})
                            amountToSell -= int(temp['newQuantity'])
                
                for entry in self.db.collection('Orders').where('simulation','==',self.sim).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock).stream():
                    if amountToSell <= 0:
                        break
                    temp = entry.to_dict()
                    averagePrice.append(float(temp['avgStockPrice']))
                    if int(temp['quantity']) - amountToSell > 0:
                        self.db.collection('Orders').document(entry.id).update({'partiallySold' : True, 'newQuantity' : abs(int(temp['quantity']) - amountToSell)})
                        amountToSell -= abs(int(temp['quantity']) - amountToSell)
                    else:
                        self.db.collection('Orders').document(entry.id).update({'sold' : True})
                        amountToSell -= int(temp['quantity'])

            return ownageFlag, mean(averagePrice)
        
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
        return [*set(tickers)]
    
    #def buyRoute(db, user, sim):
        

    def sellTaxLot(db, user, sim, orderID):
        doc = db.collection('Orders').document(orderID).get().to_dict()
        avgStockPrice = SimulationFactory(db, user).simulation.currentPriceOf(doc['ticker'])
        if doc.get('newQuantity') == None:
            count = len(db.collection('Orders').where('simulation', '==', sim).get())
            orderName = sim + doc['ticker'] + str(count)
            data = {
                'simulation': sim,
                'ticker': doc['ticker'],
                'dayOfPurchase': datetime.datetime.now(),
                'buyOrSell': 'Sell',
                'quantity': doc['quantity'],
                'avgStockPrice': avgStockPrice,
                'totalPrice': avgStockPrice * float(doc['quantity']),
                'profit': avgStockPrice * float(doc['quantity']) - float(doc['totalPrice'])
            }
            db.collection('Orders').document(orderName).set(data)
            db.collection('Orders').document(orderID).update({'sold' : True})
            Simulation.updateCash(db, sim, float(doc['totalPrice']))
            return 1
        else:
            count = len(db.collection('Orders').where('simulation', '==', sim).get())
            orderName = sim + doc['ticker'] + str(count)
            data = {
                'simulation': sim,
                'ticker': doc['ticker'],
                'dayOfPurchase': datetime.datetime.now(),
                'buyOrSell': 'Sell',
                'quantity': doc['newQuantity'],
                'avgStockPrice': avgStockPrice,
                'totalPrice': avgStockPrice * float(doc['newQuantity']),
                'profit': avgStockPrice * float(doc['newQuantity']) - float(doc['avgStockPrice']) * float(doc['newQuantity'])
            }
            db.collection('Orders').document(orderName).set(data)
            db.collection('Orders').document(orderID).update({'sold' : True, 'newQuantity' : 0})
            Simulation.updateCash(db, sim, doc['totalPrice'])
            return 1
        return -1

    # List of Orders by Muneeb Khan
    def orderList(db, simName):
        quantityOwned = 0
        ownageFlag = True

        # The order list function will loop through the orders in firebase and store each one
        # under the ordernameslist [] array. - Muneeb Khan
        orderslist = []

        if ownageFlag == True:
            for entry in db.collection('Orders').where('simulation','==',simName).stream(): # To loop through the users orders
                temp = entry.to_dict()
                date = str(datetime.datetime.fromtimestamp(temp['dayOfPurchase'].timestamp()).strftime("%Y-%m-%d %H:%M:%S"))
                if temp['buyOrSell'] == 'Buy' and temp['sold'] == False:
                    link = str('/sellTaxLot/' + entry.id)
                elif temp['buyOrSell'] == 'Buy' and temp['sold'] == True:
                    link = str('/buyOrder/' + entry.id)
                else:
                    link = ""
                if temp.get('partiallySold') != None and temp['sold'] == False:
                    partiallySold = str(temp['newQuantity'])
                else:
                    partiallySold = ""
                if temp.get('profit') != None:
                    profit = "%.2f" % round(temp['profit'],2)
                else:
                    profit = ""
                orderslist.append([temp['buyOrSell'],temp['quantity'],temp['ticker'],"%.2f" % round(float(temp['totalPrice']),2),date, partiallySold, profit, link])
            
            df = pd.DataFrame(orderslist, columns=['buyOrSell','quantity','ticker','totalPrice', 'dayOfPurchase', 'partiallySold', 'profit', 'links'])
            
            return df

class portfolio:
    def __init__(self, db, stock, user, simulation):
        self.firebase = db
        self.stock = stock
        self.user = user
        self.sim = simulation 
        self.link = str('/displayStock?ticker='+stock+'&timespan=hourly')
        self.profit, self.avgSharePrice, self.quantity = self.getVariables()
        self.volatility = 0
        self.buyForm = str('/buyOrder?ticker='+stock)
        self.sellForm = str('/stockSell?ticker='+stock)
        #self.sellForm = str('/sellForm')

    def getVariables(self):
        currentPriceOfStock = SimulationFactory(self.firebase, self.user).simulation.currentPriceOf(self.stock)
        prices = []
        avgStockPrices = []
        amountOfSharesOwned = 0
        for entry in Order.retrieve(self.firebase, self.sim, self.stock):
            temp = entry.to_dict()
            avgStockPrices.append(float(temp['avgStockPrice']))
            prices.append(float(temp['totalPrice']))
            if temp.get('newQuantity') != None:
                if temp.get('sold') != None:
                    if temp['sold'] == False:
                        amountOfSharesOwned += int(temp['newQuantity'])
            else:
                if temp.get('sold') != None:
                    if temp['sold'] == False:
                        amountOfSharesOwned += int(temp['quantity'])     
        avgPriceOfOrders = mean(prices)
        currentValueOfShares = currentPriceOfStock * amountOfSharesOwned
        if avgStockPrices:
            return currentValueOfShares - avgPriceOfOrders, mean(avgStockPrices), amountOfSharesOwned
        else:
            return currentValueOfShares - avgPriceOfOrders, 0, amountOfSharesOwned
            

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
       
    #New volatility function (Viraj Kadam)   
    def volatitlity(self):
       currentPriceOfStock = round(SimulationFactory(self.firebase, self.user).simulation.currentPriceOf(self.stock), 2)
       day = datetime.datetime.now()
       volatility = 0
       returns = 0
       prices = []
       for entry in Order.retrieveOwned(self.firebase, self.sim, self.stock):
           temp = entry.to_dict()
           returns =  np.log((prices.append(float(temp['avgStockPrice']))/(prices.append(float(temp['avgStockPrice']))).shift()))
           returns.std()
           volatility = returns.std()*225**.5
           
       return volatility
           
    #Percent change in stock per day. Part of initial push to viraj branch, will add more later tonight
    #Updated by Muneeb Khan
    def percentChange(db,simName):
 
        currentAmount = round(db.collection('IntradayStockData').document('prices').where('simulation','==',simName).where('ticker','==',db.ticker).stream())
        dates = []
        for entry in db.collection('IntradayStockData').where('simulation','==',simName).stream():
            tempdays = entry.to_dict()
            dates.append(tempdays['dates'])

        for i in dates:
            finalAmount = round(float(((currentAmount[i+1]-currentAmount[i])/currentAmount[i]) * 100),2)

        print(str(finalAmount) + " %")
        return (str(finalAmount) + " %")   
        
    #Author: Viraj Kadam    
    #Graph of user stocks   (Need buy and sell info)
    def user_graph(self, db, startDate, endDate):
        prices = self.db.collection('IntradayStockData').document('prices').get()
        dates = self.db.collection('IntradayStockData').document('dates').get()
        
        for entry in Order.retrieveOwned(self.firebase, self.sim, self.stock):
            temp = entry.to_dict()
            xlabel = prices
            ylabel = dates
            fig = plt.figure()
            plt.xlabel('Date')
            plt.ylabel('Price')
            fig = plt.plot(prices[i], dates[i])
            for i in range(db.collection('Simulations').collections('simName').collection('startDate'), db.collection('Simulations').collections('simName').collection('endDate')):
                fig[i].set_color(color[i])
            
            plt.show

## Class for setting up quiz - Muneeb Khan
## Updated by Ian Mcnulty
class Quiz:
    def __init__(self,db,quizID,user):
        self.db = db
        self.questions = self.retrieveQuestions(quizID)
        self.quizID = quizID
        self.user = user
        self.correct = []
    
    # To store all the questions and answers for the Quiz
    def retrieveQuestions(self, quizid):
        quiz = self.db.collection('Quiz').document(quizid).get().to_dict()

        questions = []
        for id in quiz['questionIds']:
            question = self.db.collection('Quiz').document(id).get().to_dict()
            questions.append([id, question['text'], question['answers'], question['correct']])

        self.questions = pd.DataFrame(questions, columns=['id','text','answers','correct'])
        return pd.DataFrame(questions, columns=['id','text','answers','correct'])

    # Check if Users answer is correct
    def answerQuestion(self, questionid, answer):
        question = self.questions.loc[self.questions['id'].isin([questionid])]
        index = self.questions[self.questions['id'] == questionid].index[0]
        correct = question['correct'].to_list()
        if answer == correct[0]:
            self.correct.append(True)

    def scoreCalc(self):
        count = len(self.correct)

        self.score = round(count, 2)
        return round(count, 2)

    def submitScore(self):
        data = {
            'user': self.user,
            'qid': self.quizID,
            'score': self.score
        }
        self.db.collection('QuizScores').add(data)

    def retrieveScore(db, user, qid):
        for entry in db.collection('QuizScores').where('user','==',user).where('qid','==',qid).stream():
            temp = entry.to_dict()
            return temp['score']

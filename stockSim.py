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
import datetime

import math

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

## Class: StockData
#   Description: Class used to manage data obtained from the Stocks collection in the database
#
#   Dependencies: firebase_admin, numpy
#
#   Authors: Ian McNulty, Muneeb Khan  
class StockData:
    ## StockData.__init__
    #   Description: Initiates a StockData object with Database and 
    #   requested stock
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
            return -1

    ## StockData.checkDate
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
            
    ## StockData.stockJSON - DEPRECATED
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

    ## StockData.retrieve
    #   Description: Retrieves data from Firestore database according
    #   to requested stock ID.
    #
    #   Inputs: id - Database key for requested stock.
    #           ticker - String, ID for stock entry
    #           startDate - String, entry for starting date of viewing period
    #           endDate - String, entry for ending date of viewing period
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

    ## StockData.stockList
    #   Description: Gets a list of available stock tickers from the Stocks collection
    #   in the database
    #
    #   Inputs: db - Link to the Firestore Database
    # 
    #   Author: Muneeb Khan
    def stockList(db):

        tickers = []

        for entry in db.collection('Stocks').get():
            tickers.append(entry.id)

        return tickers

    ## StockData.stockSearch
    #   Description: Checks to see if that stock exists in the database yet,
    #   according to the ticker and simulation ID, returns a boolean value representing
    #   whether the search term was found or not and the ticker of the stock found
    #
    #   Inputs: db - Link to the database
    #   searchTerm - String to be searched for in the database
    #   simName - ID of the simulation to be matched
    #
    #   Returns: True, if found
    #            Stock ticker String, if found
    #            False, if not found
    #            -1, if not found
    #
    #   Author: Ian McNulty
    def stockSearch(db, searchTerm, simName):

        # Search for exact match
        stocksDB = db.collection('IntradayStockData').where('simulation','==',simName)
        for entry in stocksDB.stream():
            temp = entry.to_dict()
            if temp['ticker'] == searchTerm:
                if temp.get('unavailable') != None:
                    return False, -1
                else:
                    return True, searchTerm.upper()

        # Search for string match to ticker
        for entry in stocksDB.stream():
            temp = entry.to_dict()
            ticker = temp['ticker'].lower()
            tempSearchTerm = searchTerm.lower()
            if tempSearchTerm == ticker:
                if temp.get('unavailable') != None:
                    return False, -1
                else:
                    return True, ticker.upper()

        # Search for string match to company name
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

## Class: Simulation
#   Description: Class used to manage Simulation entries and data from the Firestore database
#
#   Dependencies: firebase_admin, numpy, StockData, Order, Portfolio, SimulationFactory
#
#   Authors: Ian McNulty
class Simulation:
    ## Simulation.__init__
    #   Description: Initiates a Simulation object with inputs, not to be used to retrieve ongoing
    #   simulations
    #
    #   Inputs: db - Database object, connected to Firestore
    #           req - String, user to relate with this Simulation
    #           startDate - String, starting date of the Simulation
    #           endDate - String, ending date of the Simulation
    #           initialCash - Integer, starting amount of cash usable in this Simulation
    #
    #   Author: Ian McNulty
    def __init__(self, db, user, startDate, endDate, initialCash):
        self.db = db
        self.user = user
        self.startDate = startDate
        self.endDate = endDate
        self.initialCash = initialCash
        self.stocks = []

    ## Simulation.createSim
    #   Description: Creates an entry in the Simulations collection of the Firestore database with
    #   the input values from __init__
    #
    #   Author: Ian McNulty
    def createSim(self):
        # Starting timestamp for Simulation
        self.startTimestamp = datetime.datetime.now()

        # Dictionary for creation of the Firestore entry
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

        # Simulation ID for use in later functions, if necessary
        self.simName = tempRef.id

        # Creation of Intraday Stock Data for the Simulation
        self.addStocksToSim()

    ## Simulation.whatTimeIsItRightNow
    #   Description: Finds the correct index in the stock data by calculating the time elapsed since 
    #   starting timestamp of the Simulation creation
    #
    #   Author: Ian McNulty
    def whatTimeIsItRightNow(self):
        currentTime = datetime.datetime.now()
        difference = currentTime - self.startTimestamp
        index = -1
        total = difference.total_seconds()
        days = round(total//86400) # Days
        total -= days*86400
        hours = round(total//3600) # Hours
        total -= hours*3600
        tenMin = round(total//600) # Remaining minutes grouped in 10s
        for i in range(0,days):
            index += 40
        for i in range(0,hours):
            index += 6
        index += tenMin
        return index

    ## Simulation.addStocksToSim
    #   Description: Creates entries in the IntradayStockData collection for use in the Simulation by 
    #   using StockData.retrieve to sequentially create them
    #
    #   Author: Ian McNulty
    def addStocksToSim(self):
        tickerList = StockData.stockList(self.db)
        for ticker in tickerList:
            tempData = StockData.retrieve(self.db, ticker, self.simName, self.startDate, self.endDate)
            self.stocks.append(tempData)
            self.db.collection('IntradayStockData').add(tempData)

    ## Simulation.currentPriceOf
    #   Description: Retrieves current price of requested stock according to whatTimeIsItRightNow result
    #
    #   Input: ticker - String, ID for requested stock entry
    #
    #   Author: Ian McNulty
    def currentPriceOf(self, ticker):
        data = self.db.collection('IntradayStockData').where('simulation','==',self.simName).where('ticker','==',ticker).get()
        for entry in data:
            fin = entry.to_dict()
            highestIndex = Simulation.maxIndex(self.db, self.simName)
            if highestIndex > self.whatTimeIsItRightNow():
                return fin['prices'][self.whatTimeIsItRightNow()]
            return fin['prices'][len(fin['prices'])-1]

    ## Simulation.retrieveStock
    #   Description: Retrieves database entry matching Simulation ID and ticker ID
    #
    #   Input: ticker - String, ID for requested stock entry
    #
    #   Author: Ian McNulty
    def retrieveStock(self, ticker):
        stock = self.db.collection('IntradayStockData').where('simulation','==',self.simName).where('ticker','==',ticker).get()
        return stock

    ## Simulation.amountOwned
    #   Description: Retrieves currently owned amount of shares of a searched stock
    #
    #   Input: ticker - String, ID for requested stock entry
    #
    #   Author: Ian McNulty
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

    ## Simulation.finishSimulation
    #   Description: Calculates score based on final valuation of Portfolio combined with
    #   current amount of cash available to the user, it then marks the simulation as 
    #   finished and stores the score
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           simName - String, ID of the simulation data entry to be finished
    #
    #   Author: Ian McNulty
    def finishSimulation(db, simName):
        data = db.collection('Simulations').document(simName).get().to_dict()

        quantities = []
        currentPrices = []
        totalValue = 0
        
        # Retrieve current values of owned shares
        for entry in Order.stocksBought(db, simName):
            portfolio = Portfolio(db, entry, data['user'], simName)
            if portfolio.quantity != 0:
                quantities.append(portfolio.quantity)
                currentPrices.append(round(SimulationFactory(db, data['user']).simulation.currentPriceOf(entry), 2))
        
        # Summation of Portfolio value
        for i in range(len(quantities)):
            totalValue += quantities[i] * currentPrices[i]

        # Score calculation
        percentChange = ((float(data['currentCash']) + totalValue) - float(data['initialCash'])) / float(data['initialCash'])
        scores = percentChange * 100
        scoreRounded = round(scores)
        grabDataEmail = data['user']
        userEmail = db.collection('Users').where('Email', '==', grabDataEmail)
        for docs in userEmail.stream():
                emails = docs.to_dict()
        grabUserName = emails['userName']

        # Leaderboard data entry calculation
        db.collection('Leaderboard').add({"email":grabDataEmail, "score":scoreRounded, "username":grabUserName})

        # Delete newly useless entries in the IntradayStockData entries associated with finished Sim
        for entry in db.collection('IntradayStockData').where('simulation','==',simName).stream():
            temp = entry.id
            db.collection('IntradayStockData').document(temp).delete()

        # Add score to Simulation entry and mark it as finished
        data['score'] = percentChange * 100
        data['ongoing'] = False
        db.collection('Simulations').document(simName).update(data)

    ## Simulation.checkDates
    #   Description: Compares the input dates to confirm that the start date comes
    #   before the end date
    #
    #   Inputs: startDate - String, starting date to be checked
    #           endDate - String, ending date to be checked
    #
    #   Return: True, if dates are a valid input
    #           False, if dates are an invalid input
    #   
    #   Author: Ian McNulty
    def checkDates(startDate, endDate):
        if int(startDate[0:4]) >= int(endDate[0:4]):
            if int(startDate[5:7]) > int(endDate[5:7]):
                return False
            elif int(startDate[5:7]) == int(endDate[5:7]):
                if int(startDate[8:10]) >= int(endDate[8:10]):
                    return False
        return True

    ## Simulation.retrieveOngoing
    #   Description: Retrieves the currently ongoing simulation given an ID
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           user - String, ID of the user to be searched for in the Simulation collection
    #
    #   Return: tempSim - Dictionary, dict object in the form of the Simulation data entry
    #
    #   Author: Ian McNulty
    def retrieveOngoing(db, user):
        for query in db.collection('Simulations').where('ongoing','==',True).where('user','==',user).stream():
            id = query.id
            entry = query.to_dict()

        tempSim = Simulation(db, user, entry['startDate'], entry['endDate'], entry['initialCash'])
        tempSim.simName = id
        tempSim.startTimestamp = datetime.datetime.fromtimestamp(entry['startTimestamp'].timestamp())
        tempSim.currentCash = round(float(entry['currentCash']), 2)
        tempSim.initialCash = entry['initialCash']
        tempSim.stocks = []
        for entry in db.collection('IntradayStockData').where('simulation','==',id).stream():
            temp = entry.to_dict()
            tempSim.stocks.append(temp)

        return tempSim
    
    ## Simulation.updateCash
    #   Description: Updates the currently available amount of cash in the simulation by
    #   adding the amount of change to it
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           simName - String, ID of the simulation data entry
    #           delta - Float, amount to update the currently available cash by
    #
    #   Author: Ian McNulty
    def updateCash(db, simName, delta):
        data = db.collection('Simulations').document(simName).get().to_dict()
        currentCash = data['currentCash']
        newCurrentCash = float(currentCash) + float(delta)
        db.collection('Simulations').document(simName).update({'currentCash' : newCurrentCash})

    ## Simulation.retrieveCurrentCash - DEPRECATED
    #   Description: Retrieves the available amount of cash to the user in the simulation
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           simName - String, ID of the simulation data entry
    #
    #   Return: data['currentCash'] - Float, currently available amount of cash to the user
    #
    #   Author: Ian McNulty
    def retrieveCurrentCash(db, simName):
        data = db.collection('Simulations').document(simName).get().to_dict()
        return data['currentCash']

    ## Simulation.maxIndex
    #   Description: Calculates the highest index found in the IntradayStockData collection for
    #   the simulation's associated stocks; to be used with time limit checking for simulation
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           simName - String, ID of the simulation data entry
    #
    #   Return: highestIndex - Integer, highest index found in the IntradayStockData for the sim
    #
    #   Author: Ian McNulty
    def maxIndex(db, simName):
        highestIndex = 0
        for entry in db.collection('IntradayStockData').where('simulation','==',simName).stream():
            temp = entry.to_dict()
            if temp.get('unavailable') == None:
                if len(temp['prices']) > highestIndex:
                    highestIndex = len(temp['prices'])
        return highestIndex

    ## Simulation.ongoingCheck
    #   Description: Checks to see if there is a currently ongoing simulation associated with the 
    #   user
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           simName - String, ID of the simulation data entry
    #           user - String, ID of the user to be checked
    #
    #   Return: True, if ongoing simulation found
    #           False, if ongoing simulation not found
    #
    #   Author: Ian McNulty
    def ongoingCheck(db, simName, user):
        index = SimulationFactory(db, user).simulation.whatTimeIsItRightNow()        
        highestIndex = Simulation.maxIndex(db,simName)
        if index > highestIndex:
            return False
        return True

    ## Simulation.listSims
    #   Description: Retrieves the IDs, starting dates, scores, and links to order history of 
    #   all finished sims for the user
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           user - String, ID of the user to be checked
    #
    #   Return: sims - String array, IDs of the listed simulations
    #           dates - String array, starting dates of the listed simulations
    #           scores - Float array, scores of the listed simulations
    #           links - String array, redirects to order history of the listed simulations
    #
    #   Author: Ian McNulty
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

    ## Simulation.completedCheck - DEPRECATED
    #   Description: Checks if the user has completed simulations
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           user - String, ID of the user to be checked
    #
    #   Return: True, if completed simulation found
    #           False, if completed simulation not found
    #
    #   Author: Ian McNulty
    def completedCheck(db, user):
        count = 0
        for query in db.collection('Simulations').where('ongoing','==',False).where('user','==',user).stream():
            count += 1
        if count >= 1:
            return True
        return False

    ## Simulation.getPortfolioValue
    #   Description: Calculates the current Portfolio value and gives it to the user along with
    #   the current cash amount available to the user
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           simName - String, ID of the simulation data entry to be finished
    #
    #   Return: totalValue - Float, total value of the Portfolio, in USD
    #           data['currentCash'] - Float, currently available amount of cash to the user
    #               in this simulation
    #
    #   Author: Ian McNulty
    def getPortfolioValue(db, simName):
        quantities = []
        currentPrices = []
        totalValue = 0
        data = db.collection('Simulations').document(simName).get().to_dict()
        
        for entry in Order.stocksBought(db, simName):
            portfolio = Portfolio(db, entry, data['user'], simName)
            if portfolio.quantity != 0:
                quantities.append(portfolio.quantity)
                currentPrices.append(round(SimulationFactory(db, data['user']).simulation.currentPriceOf(entry), 2))
        
        for i in range(len(quantities)):
            totalValue += quantities[i] * currentPrices[i]

        return totalValue, data['currentCash']

    ## Simulation.getAvailableStockList
    #   Description: Retrieves the tickers, prices, redirect links, and names of the companies
    #   currently available to the user in their simulation
    #
    #   Inputs: db - Firestore object, link to Firestore database
    #           simName - String, ID of the simulation data entry to be finished
    #           user - String, ID of the user associated with the Simulation
    #
    #   Return: tickers - String array, tickers of the available stocks in the sim
    #           prices - Float array, current prices of the available stocks in the sim
    #           links - String array, redirects to display of available stocks in the sim
    #           names - String array, company names of available stocks in the sim
    #
    #   Author: Ian McNulty
    def getAvailableStockList(db, simName, user):
        index = SimulationFactory(db, user).simulation.whatTimeIsItRightNow()        
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

## Class: SimulationFactory
#   Description: Class used to create Simulation objects by retrieving the currently ongoing 
#   simulation associated with the user
#
#   Dependencies: Simulation
#
#   Authors: Ian McNulty
class SimulationFactory:
    ## SimulationFactory.__init__
    #   Description: Retrieves the ongoing simulation data with only a user ID as a key
    # 
    #   Inputs: db - String, link to the Firestore database
    #           user - String, ID of the user to be searched for
    #
    #   Author: Ian McNulty
    def __init__(self, db, user):
        self.simulation = Simulation.retrieveOngoing(db, user)

    ## SimulationFactory.existenceCheck
    #   Description: Checks whether there is an ongoing simulation for the given user
    # 
    #   Inputs: db - String, link to the Firestore database
    #           user - String, ID of the user to be searched for
    #
    #   Return: True, if ongoing simulation exists
    #           False, if ongoing simulation does not exist
    #
    #   Author: Ian McNulty
    def existenceCheck(db, user):
        array = [entry for entry in db.collection('Simulations').where('ongoing','==',user).where('user','==',email).stream()]
        if len(array) == 0:
            return False, "None"
        else:
            return True, array[0].id

## Class: User
#   Description: Class used to handle and change User data within the application
#
#   Dependencies: firebase_admin, numpy, StockData, Order, Portfolio, SimulationFactory
#
#   Authors: Ian McNulty, Muneeb Khan
class User:
    ## User.__init__
    #   Description: Creates an object of User type with the given inputs
    # 
    #   Inputs: db - String, link to the Firestore database
    #           user - String, ID of the user to be created
    #
    #   Author: Ian McNulty
    def __init__(self, db, user):
        self.db = db
        self.user = user
        self.userDataDocument = self.retrieve()
        if self.userDataDocument != 'This data entry does not exist':
            self.email = self.userDataDocument['Email']
            self.userID = self.userDataDocument['UserID']
            self.description = self.userDataDocument['Description']
            self.picture = self.userDataDocument['Picture']
            self.experience = self.userDataDocument['Experience']
        else:
            print("This user does not exist")

    ## User.retrieve
    #   Description: Retrieves the user from the Firestore database
    # 
    #   Return: 'This data entry does not exist', if the user is not found
    #           self.db.collection('Users').document(self.user).get(), if the user is found
    #
    #   Author: Ian McNulty
    def retrieve(self):
        try:
            return self.db.collection('Users').document(self.user).get()
        except:
            return 'This data entry does not exist'

    ## User.updateProfile
    #   Description: Updates the profile entry in the database with the given parameters
    # 
    #   Inputs: description - String, new description of the user
    #           picture - Photo (JPG, PNG, etc), new profile photo for the user
    #           experience - String, new experience description of the user
    #
    #   Author: Ian McNulty
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

    ## User.updateDescription
    #   Description: Updates the description field in the User entry
    # 
    #   Inputs: description - String, new description of the user
    #
    #   Author: Ian McNulty
    def updateDescription(self, description):
        data = self.db.collection("Users").document(self.user)
        data.update({ 'Description' : description })

    ## User.updatePicture
    #   Description: Updates the profile photo field in the User entry
    # 
    #   Inputs: picture - Photo (JPG, PNG, etc), new profile photo for the user
    #
    #   Author: Ian McNulty
    def updatePicture(self, picture):
        data = self.db.collection("Users").document(self.user)
        data.update({ 'Picture' : picture })

    ## User.updateExperience
    #   Description: Updates the experence field in the User entry
    # 
    #   Inputs: experience - String, new experience description of the user
    #
    #   Author: Ian McNulty
    def updateExperience(self, experience):
        data = self.db.collection("Users").document(self.user)
        data.update({ 'Experience' : experience })

    ## User.registerUser
    #   Description: Registers a user data entry with the given inputs
    # 
    #   Inputs: db - String, link to the Firestore database
    #           username - String, username of the user
    #           email - String, email of the user
    #           name - String, name of the user
    #           userID - String, ID of the user
    #           description - String, new description of the user
    #           picture - Photo (JPG, PNG, etc), new profile photo for the user
    #           experience - String, new experience description of the user
    #
    #   Author: Ian McNulty
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

    ## User.userList
    #   Description: Lists the user values for viewing on the front end
    # 
    #   Inputs: db - String, link to the Firestore database
    #
    #   Author: Ian McNulty, Muneeb Khan
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

## Class: Order
#   Description: Class used to handle and change Order data from the application
#
#   Dependencies: firebase_admin, numpy, Simulation, SimulationFactory
#
#   Authors: Ian McNulty, Muneeb Khan
class Order:
    ## Order.__init__
    #   Description: Creates an object of Order type to be able to add it to the Orders collection in
    #   the Firestore database
    # 
    #   Inputs: db - String, link to the Firestore database
    #           simName - String, ID of the associated simulation
    #           stock - String, ID of the associated stock
    #           buyOrSell - String, type of order to be created
    #           quantity - Integer, amount of shares to be bought or sold
    #           stockPrice - Float, price of the stock at time of purchase
    #
    #   Author: Ian McNulty
    def __init__(self, db, simName, stock, buyOrSell, quantity, stockPrice):
        self.db = db
        self.simName = simName
        self.stock = stock
        self.dayOfPurchase = datetime.datetime.now()
        self.option = buyOrSell
        self.quantity = quantity
        self.avgStockPrice = stockPrice
        self.totalPrice = float(quantity)*float(stockPrice)

    ## Order.buyOrder
    #   Description: Creates a buy order if the user has enough money
    #
    #   Author: Ian McNulty
    def buyOrder(self):
        if self.option == 'Buy':
            if self.doTheyHaveEnoughMoney():
                count = len(self.db.collection('Orders').where('simulation', '==', self.simName).get())
                orderName = self.simName + self.stock + str(count)
                data = {
                    'sold': False,
                    'simulation': self.simName,
                    'ticker': self.stock,
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'Buy',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice
                }
                self.db.collection('Orders').document(orderName).set(data)
                Simulation.updateCash(self.db, self.simName, float(self.totalPrice) * -1)
                return 1
            else: return -1

    ## Order.sellOrder
    #   Description: Creates a sell order if the user has enough shares
    #
    #   Author: Ian McNulty
    def sellOrder(self):
        if self.option == 'Sell':
            check, averagePrice = self.doTheyOwnThat()
            if check == True:
                count = len(self.db.collection('Orders').where('simulation', '==', self.simName).get())
                orderName = self.simName + self.stock + str(count)
                data = {
                    'simulation': self.simName,
                    'ticker': self.stock,
                    'dayOfPurchase': self.dayOfPurchase,
                    'buyOrSell': 'Sell',
                    'quantity': self.quantity,
                    'avgStockPrice': self.avgStockPrice,
                    'totalPrice': self.totalPrice,
                    'profit': float(self.avgStockPrice)*float(self.quantity) - float(averagePrice)*float(self.quantity)
                }
                self.db.collection('Orders').document(orderName).set(data)
                Simulation.updateCash(self.db, self.simName, self.totalPrice)
                return 1
            else: return -1

    ## Order.doTheyHaveEnoughMoney
    #   Description: Checks if the user has enough money to buy the requested amount of shares
    #
    #   Author: Ian McNulty
    def doTheyHaveEnoughMoney(self):
        enoughFlag = False

        currentCash = int(self.db.collection('Simulations').document(self.simName).get().to_dict()['currentCash'])
        if currentCash >= self.totalPrice:
            enoughFlag = True

        return enoughFlag

    ## Order.doTheyOwnThat
    #   Description: Checks if the user owns the shares they are trying to sell
    #
    #   Author: Ian McNulty
    def doTheyOwnThat(self):
        quantityOwned = 0
        ownageFlag = False
        partialFlag = False
        # Retrieve buy orders
        for entry in self.db.collection('Orders').where('simulation','==',self.simName).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock).get():
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
                # Partial order sales go first
                if partialFlag == True:
                    for entry in self.db.collection('Orders').where('simulation','==',self.simName).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock).where('partiallySold','==',True).stream():
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
                
                # Whole order sales go second
                for entry in self.db.collection('Orders').where('simulation','==',self.simName).where('buyOrSell','==','Buy').where('sold','==',False).where('ticker','==',self.stock).stream():
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

    ## Order.retrieve
    #   Description: Retrieves all orders associated with the simulation and ticker
    # 
    #   Inputs: db - String, link to the Firestore database
    #           simName - String, ID of the simulation data entry
    #           ticker - String, ID of the stock to be affected
    #
    #   Author: Ian McNulty
    def retrieve(db, simName, ticker):
        return db.collection('Orders').where('simulation','==',simName).where('ticker','==',ticker).stream()

    ## Order.retrieveOwned
    #   Description: Retrieves all unsold buy orders associated with the simulation and ticker
    # 
    #   Inputs: db - String, link to the Firestore database
    #           simName - String, ID of the simulation data entry
    #           ticker - String, ID of the stock to be affected
    #
    #   Author: Ian McNulty
    def retrieveOwned(db, simName, ticker):
        return db.collection('Orders').where('simulation','==',simName).where('ticker','==',ticker).where('sold','==',False).stream()

    ## Order.stocksBought
    #   Description: Retrieve list of stocks bought in the associated simulation
    # 
    #   Inputs: db - String, link to the Firestore database
    #           simName - String, ID of the simulation data entry
    #
    #   Author: Ian McNulty
    def stocksBought(db, simName):
        tickers = []
        for entry in db.collection('Orders').where('simulation','==',simName).stream():
            temp = entry.to_dict()
            tickers.append(temp['ticker'])
        return [*set(tickers)]

    ## Order.sellTaxLot
    #   Description: Sells all remaining shares of a specific order
    # 
    #   Inputs: db - String, link to the Firestore database
    #           simName - String, ID of the simulation data entry
    #           ticker - String, ID of the stock to be affected
    #           orderID - String, ID of the order to be sold
    #
    #   Author: Ian McNulty
    def sellTaxLot(db, user, simName, orderID):
        doc = db.collection('Orders').document(orderID).get().to_dict()
        avgStockPrice = SimulationFactory(db, user).simulation.currentPriceOf(doc['ticker'])
        if doc.get('newQuantity') == None:
            count = len(db.collection('Orders').where('simulation', '==', simName).get())
            orderName = simName + doc['ticker'] + str(count)
            data = {
                'simulation': simName,
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
            Simulation.updateCash(db, simName, float(doc['totalPrice']))
            return 1
        else:
            count = len(db.collection('Orders').where('simulation', '==', simName).get())
            orderName = simName + doc['ticker'] + str(count)
            data = {
                'simulation': simName,
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
            Simulation.updateCash(db, simName, doc['totalPrice'])
            return 1

    ## Order.orderList
    #   Description: Lists the order values for viewing on the front end
    # 
    #   Inputs: db - String, link to the Firestore database
    #           simName - String, ID for the current simulation
    #
    #   Author: Ian McNulty, Muneeb Khan
    def orderList(db, simName):
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

## Class: Portfolio
#   Description: Class used to handle and concatenate relevant ownership data for the user in the front end
#
#   Dependencies: firebase_admin, numpy, StockData, Order, Portfolio, SimulationFactory
#
#   Authors: Viraj Kadam, Ian McNulty, Muneeb Khan
class Portfolio:
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

## Class: Quiz
#   Description: Class used to handle questions and answers for quizzes taken by the user
#
#   Dependencies: firebase_admin, pandas
#
#   Authors: Muneeb Khan, Ian McNulty
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

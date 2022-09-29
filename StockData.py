import numpy as np
import Order, User

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
                    
                    return -1
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

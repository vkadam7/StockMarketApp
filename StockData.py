import numpy as np

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
        self.firebase = db.database
        self.ticker = req
        self.data = self.retrieve(self.ticker)
        if self.data != 'This data entry does not exist':
            self.name = self.data['name']
            self.headquarters = self.data['headquarters']
            self.listedAt = self.data['listedAt']
            self.dates = self.data['dates']
            self.opens = self.data['opens']
            self.highs = self.data['highs']
            self.lows = self.data['lows']
            self.closes = self.data['closes']
            self.adjCloses = self.data['adjustedCloses']
            self.volumes = self.data['volumes']
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

    def getData(self, start, end):
        try:
            dataMatrix = []
            tempArr = np.array(self.dates)
            startLoc = np.where(tempArr == start)
            endLoc = np.where(tempArr == end)
            for i in range(startLoc, endLoc+1):
                dataMatrix.append([self.dates[i], self.opens[i], self.highs[i],
                                   self.lows[i], self.closes[i], self.adjCloses[i],
                                   self.volumes[i]])
            return dataMatrix
        except:
            print("An exception has been thrown")

import numpy as np
import plotly
import plotly.graph_objects as graph
import pandas as pd

def doesThatStockExist(db, ticker):
    tempData = db.child('Stocks').child(ticker).get().val() 
    if tempData == None:
        return False
    else:
        return True

class StockData:
    ## StockData __init__
    #   Description: Initiates a StockData object with Database and 
    #   requested stock, for display
    #
    #   Inputs: db - Database object, connected to Firestore
    #           req - Key for requested stock
    #           timeMeasure - Which timespan measure was chosen? 
    #           'daily', 'weekly', or 'monthly'?
    #
    #   Author: Ian McNulty
    def __init__(self, db, req, timeMeasure):
        self.firebase = db
        self.ticker = req
        self.data = self.retrieve(self.ticker)
        if self.data != 'This data entry does not exist':
            self.name = self.data['name']
            self.headquarters = self.data['headquarters']
            self.listedAt = self.data['listedAt']
            self.howLong(timeMeasure)
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

    def getData(self, start, end, timeMeasure):
        try:
            dataMatrix = []
            tempArr = np.array(self.dates)
            startLoc = np.where(tempArr == start)
            endLoc = np.where(tempArr == end)
            for i in range(startLoc[0][0], endLoc[0][0]+1):
                dataMatrix.append([self.dates[i], self.opens[i], self.highs[i],
                                   self.lows[i], self.closes[i], self.adjCloses[i],
                                   self.volumes[i]])
            return dataMatrix
        except IndexError:
            print("One of the selected dates are unavailable")

    def howLong(self, timeMeasure):
        tempData = self.data[timeMeasure]
        self.dates = tempData['dates']
        self.opens = tempData['opens']
        self.highs = tempData['highs']
        self.lows = tempData['lows']
        self.closes = tempData['closes']
        self.adjCloses = tempData['adjustedCloses']
        self.volumes = tempData['volumes']

    def stockPageFactory(self):
        chart = [graph.Scatter(x=self.dates,y=self.closes)]
        mapping = graph.Layout(xaxis=dict(title='Date'),yaxis=dict(title="Closing Price"))
        fig = graph.Figure(data=chart,layout=mapping)

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

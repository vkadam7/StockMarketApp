## UploadScript
#   Description: Uploads a stock's information to the real time database at Firestore
#   
#   Inputs: Until we add some more info to each stock, you need the ticker, company
#   name, headquarters, listing location, and a CSV file containing the historical 
#   data for the specified stock
#
#   Author: Ian McNulty
from main import firebase, app
import csv
import pyrebase
import numpy as np

ticker = 'GOOG'
name = 'Alphabet, Inc'
headquarters = 'Mountain View, CA'
listedAt = 'NASDAQ'
fileToOpen = 'GOOG.csv'

db = firebase.database()

file = open(fileToOpen)
csvreader = csv.reader(file)
header = next(csvreader)

dates = []
opens = []
highs = []
lows = []
closes =[]
adjCloses = []
volumes = []
for row in csvreader:
    dates.append(row[0])
    opens.append(float(row[1]))
    highs.append(float(row[2]))
    lows.append(float(row[3]))
    closes.append(float(row[4]))
    adjCloses.append(float(row[5]))
    volumes.append(float(row[6]))

data = {
    'name': name,
    'headquarters': headquarters,
    'listedAt': listedAt,
    'dates': dates,
    'opens': opens,
    'highs': highs,
    'lows': lows,
    'closes': closes,
    'adjustedCloses': adjCloses,
    'volumes': volumes
}
db.child('Stocks').child(ticker).set(data)




# Testing Location
temp = db.child("Stocks").child(ticker).get().val()
print(temp['dates'][1])
tempArr = np.array(temp['dates'])
loc = np.where(tempArr == '2020-02-03')
print(loc[0][0])
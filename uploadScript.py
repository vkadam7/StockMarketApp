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

ticker = 'AMZN'
name = 'Amazon.com, Inc'
headquarters = 'Seattle, WA'
listedAt = 'NASDAQGS'
fileToOpen = 'stockdata/AMZN.csv'

db = firebase.database()

file = open(fileToOpen)
csvreader = csv.reader(file)
header = next(csvreader)

# Daily data extractor
datesD = []
opensD = []
highsD = []
lowsD = []
closesD =[]
adjClosesD = []
volumesD = []
for row in csvreader:
    datesD.append(row[0])
    opensD.append(float(row[1]))
    highsD.append(float(row[2]))
    lowsD.append(float(row[3]))
    closesD.append(float(row[4]))
    adjClosesD.append(float(row[5]))
    volumesD.append(float(row[6]))


data = {
    'name': name,
    'headquarters': headquarters,
    'listedAt': listedAt,
    'daily': {'dates': datesD, 'opens': opensD, 'highs': highsD,
                'lows': lowsD, 'closes': closesD, 'adjustedCloses': adjClosesD,
                'volumes': volumesD}
}
db.child('Stocks').child(ticker).set(data)
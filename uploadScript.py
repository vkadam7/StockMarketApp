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
fileToOpen = 'GOOGdaily.csv'

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

fileToOpen = 'GOOGweekly.csv'
file = open(fileToOpen)
csvreader = csv.reader(file)
header = next(csvreader)

# Weekly data extractor
datesW = []
opensW = []
highsW = []
lowsW = []
closesW =[]
adjClosesW = []
volumesW = []
for row in csvreader:
    datesW.append(row[0])
    opensW.append(float(row[1]))
    highsW.append(float(row[2]))
    lowsW.append(float(row[3]))
    closesW.append(float(row[4]))
    adjClosesW.append(float(row[5]))
    volumesW.append(float(row[6]))

fileToOpen = 'GOOGmonthly.csv'
file = open(fileToOpen)
csvreader = csv.reader(file)
header = next(csvreader)

# Monthly data extractor
datesM = []
opensM = []
highsM = []
lowsM = []
closesM =[]
adjClosesM = []
volumesM = []
for row in csvreader:
    datesM.append(row[0])
    opensM.append(float(row[1]))
    highsM.append(float(row[2]))
    lowsM.append(float(row[3]))
    closesM.append(float(row[4]))
    adjClosesM.append(float(row[5]))
    volumesM.append(float(row[6]))

data = {
    'name': name,
    'headquarters': headquarters,
    'listedAt': listedAt,
    'daily': {'dates': datesD, 'opens': opensD, 'highs': highsD,
                'lows': lowsD, 'closes': closesD, 'adjustedCloses': adjClosesD,
                'volumes': volumesD} ,
    'weekly': {'dates': datesW, 'opens': opensW, 'highs': highsW,
                'lows': lowsW, 'closes': closesW, 'adjustedCloses': adjClosesW,
                'volumes': volumesW} ,
    'monthly': {'dates': datesM, 'opens': opensM, 'highs': highsM,
                'lows': lowsM, 'closes': closesM, 'adjustedCloses': adjClosesM,
                'volumes': volumesM} 
}
db.child('Stocks').child(ticker).set(data)


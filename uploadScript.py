## UploadScript
#   Description: Uploads a stock's information to the real time database at Firestore
#   
#   Inputs: Until we add some more info to each stock, you need the ticker, company
#   name, headquarters, listing location, and a CSV file containing the historical 
#   data for the specified stock
#
#   Author: Ian McNulty
import csv
import numpy as np
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin

cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client() #firestore database

ticker = 'DB'
name = "Deutsche Bank Aktiengesellschaft"
headquarters = 'Frankfurt am Main, Germany'
listedAt = 'NYSE'
fileToOpen = 'stockData/DB.csv'

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
db.collection('Stocks').document(ticker).set(data)

stockSearchData = {
    'name': name,
    'headquarters': headquarters,
    'listedAt': listedAt
}
db.collection('StockSearchInfo').document(ticker).set(stockSearchData)

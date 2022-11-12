## QuizUploadScript
#
#   Author: Ian McNulty
import numpy as np
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client() #firestore database

questions = [
{ # Question 1
    'text' : '',
    'text' : 'What is a Shareholder?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'A person who shares investments across different companies',
        'b' : 'A person who owns at least one share of a companys stock',
        'c' : 'A person who sells a companies stock to another shareholder'
    },
    'correct' : 'a'
    'correct' : 'b'
},
{ # Question 2
    'text' : '',
    'text' : 'What is the best way to start investments?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'Paper trading',
        'b' : 'Bitcoin trading',
        'c' : 'Selling'
    },
    'correct' : 'a'
},
{ # Question 3
    'text' : '',
    'text' : 'What is the name of our website?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'StockMarket',
        'b' : 'StockSim',
        'c' : 'StockTrades'
    },
    'correct' : 'a'
    'correct' : 'b'
},
{ # Question 4
    'text' : '',
    'text' : 'What is Arbitrage?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'Taking advantage of a small price difference',
        'b' : 'Selling a stock',
        'c' : 'The measure of how easy it is to buy or sell a stock'
    },
    'correct' : 'a'
},
{ # Question 5
    'text' : '',
    'text' : 'Which of the following is an investors records of stocks bought and sold in a period of time?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'High',
        'b' : 'Order',
        'c' : 'Portfolio'
    },
    'correct' : 'a'
    'correct' : 'c'
},
{ # Question 6
    'text' : '',
    'text' : 'What is a share?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'A coupon to the company store',
        'b' : 'A ticket to become the CEO',
        'c' : 'A portion of ownership of a company'
    },
    'correct' : 'a'
    'correct' : 'c'
}, 
{ # Question 7
    'text' : '',
    'text' : 'What is the number one rule of stock trading?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'Buy low, sell high',
        'b' : 'Buy high, sell low',
        'c' : 'The only way to win is not to play'
    },
    'correct' : 'a'
},
{ # Question 8
    'text' : '',
    'text' : 'What is a dividend?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'A share of a company',
        'b' : 'A portion of a stock',
        'c' : 'A payout from the company for shareholders'
    },
    'correct' : 'a'
    'correct' : 'c'
}, 
{ # Question 9
    'text' : '',
    'text' : 'What is volatility?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'A statistical measure of how much a stock stays the same',
        'b' : 'A statistical measure of how much a stock moves up or down',
        'c' : 'A statistical measure of how little a stock moves up or down'
    },
    'correct' : 'a'
    'correct' : 'b'
},
{ # Question 10
    'text' : '',
    'text' : 'What is yield?',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
        'a' : 'The amount of return on an investment',
        'b' : 'The amount of shares you hold in a stock',
        'c' : 'A type of American road sign'
    },
    'correct' : 'a'
}]

ids = []
for entry in questions:
   temp = db.collection('Quiz').add(entry)
   ids.append(temp.id)
   temp, tempID = db.collection('Quiz').add(entry)
   ids.append(tempID.id)

quiz = {
    'questionIds': ids
}

quizName = 'Tester'
# Name of quiz entry
quizName = 'Quiz1'
db.collection('Quiz').document(quizName).set(quiz)
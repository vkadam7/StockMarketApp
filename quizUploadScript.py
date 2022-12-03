## QuizUploadScript
#
#   Author: Ian McNulty
#   Update by Muneeb Khan
import numpy as np
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin

cred = credentials.Certificate("serviceAccountKey.json")
app = firebase_admin.initialize_app(cred)
db = firestore.client() #firestore database

questions = [
{ # Question 1
    'text' : 'What is an Index?',
    'answers' : {
        'a' : 'A point on the stock graph to indicate the amount',
        'b' : 'A companys highest price point for the day',
        'c' : 'A companys lowest price point for the day'
    },
    'correct' : 'a'
},
{ # Question 2
    'text' : 'What is a Market order?',
    'answers' : {
        'a' : 'An order that is bought from a store',
        'b' : 'An order that is bought based on the companys price',
        'c' : 'An order that is bought based on the markets price'
    },
    'correct' : 'c'
},
{ # Question 3
    'text' : 'What is a liquidity?',
    'answers' : {
        'a' : 'The measure of how much time it takes to buy a stock',
        'b' : 'Taking advantage of a big price difference',
        'c' : 'The measure of how easy it is to buy or sell a stock'
    },
    'correct' : 'c'
},
{ # Question 4
    'text' : 'What is an ownership of a part of the companies investments?',
    'answers' : {
        'a' : 'Stocks',
        'b' : 'Yields',
        'c' : 'Volatility'
    },
    'correct' : 'a'
},
{ # Question 5
    'text' : 'Who was the founder of stocks?',
    'answers' : {
        'a' : 'Benjamin Franklin',
        'b' : 'The Dutch East India Company',
        'c' : 'New York Stock exchange'
    },
    'correct' : 'b'
},
{ # Question 6
    'text' : 'For dividends what is the cut off date before the record date called?',
    'answers' : {
        'a' : 'Dividend date',
        'b' : 'Ex-dividend date',
        'c' : 'Dividend reinvestment date'
    },
    'correct' : 'b'
}, 
{ # Question 7
    'text' : 'Which of the following usually have high liquidity',
    'answers' : {
        'a' : 'Cash & stocks',
        'b' : 'Real estates',
        'c' : 'Interest rates'
    },
    'correct' : 'a'
},
{ # Question 8
    'text' : 'What is the highest point of a companys price called?',
    'answers' : {
        'a' : 'Open',
        'b' : 'Max',
        'c' : 'High'
    },
    'correct' : 'c'
}, 
{ # Question 9
    'text' : 'Stock graphs can be displayed as',
    'answers' : {
        'a' : 'Line charts',
        'b' : 'Bar charts',
        'c' : 'Pie charts',
        'd' : 'all of the above',
        'e' : 'a & b only'
    },
    'correct' : 'e'
},
{ # Question 10
    'text' : 'What is the ticker for the Walt Disney company?',
    'answers' : {
        'a' : 'DISNE',
        'b' : 'DI',
        'c' : 'DISN',
        'd' : 'DIS'
    },
    'correct' : 'd'
},

{
    #Question 11
    'text': 'How long is the stock market opened till?',
    'answers': {
        'a': '10AM-5PM',
        'b': '9AM-5PM',
        'c': '12PM-10PM',
        'd': '24/7'
    }, 
    'correct': 'b'
}]

ids = []
for entry in questions:
   temp, tempID = db.collection('Quiz').add(entry)
   ids.append(tempID.id)

quiz = {
    'questionIds': ids
}

# Name of quiz entry
quizName = 'Quiz2'
db.collection('Quiz').document(quizName).set(quiz)


questions2 = [
{
    #Question 1
    'text': 'What does a portfolio contain?',
    'answers': {
        'a': 'Your holdings',
        'b': 'Stock Buy Options',
        'c': 'Profits/Losses',
        'd': 'All of the above',
        },
    
    'correct': 'd'
},            
{
    #Question 2
    'text':'',
    'answers': {
        'a': '',
        'b': '',
        'c': '',
        'd': '',
    },
    
    'correct': ''  
},

{ # Question 3
    'text' : 'What is an ownership of a part of the companies investments?',
    'answers' : {
        'a' : 'Stocks',
        'b' : 'Yields',
        'c' : 'Volatility'
    },
    'correct' : 'a'
},
{ # Question 4
    'text' : 'Who was the founder of stocks?',
    'answers' : {
        'a' : 'Benjamin Franklin',
        'b' : 'The Dutch East India Company',
        'c' : 'New York Stock exchange'
    },
    'correct' : 'b'
},
{ # Question 5
    'text' : 'For dividends what is the cut off date before the record date called?',
    'answers' : {
        'a' : 'Dividend date',
        'b' : 'Ex-dividend date',
        'c' : 'Dividend reinvestment date'
    },
    'correct' : 'b'
}, 
{ # Question 6
    'text' : 'Which of the following usually have high liquidity',
    'answers' : {
        'a' : 'Cash & stocks',
        'b' : 'Real estates',
        'c' : 'Interest rates'
    },
    'correct' : 'a'
},
{ # Question 7
    'text' : 'What is the highest point of a companys price called?',
    'answers' : {
        'a' : 'Open',
        'b' : 'Max',
        'c' : 'High'
    },
    'correct' : 'c'
}, 
{ # Question 8
    'text' : 'Stock graphs can be displayed as',
    'answers' : {
        'a' : 'Line charts',
        'b' : 'Bar charts',
        'c' : 'Pie charts',
        'd' : 'all of the above',
        'e' : 'a & b only'
    },
    'correct' : 'e'
},
{ # Question 9
    'text' : 'What is the ticker for the Walt Disney company?',
    'answers' : {
        'a' : 'DISNE',
        'b' : 'DI',
        'c' : 'DISN',
        'd' : 'DIS'
    },
    'correct' : 'd'
}
]


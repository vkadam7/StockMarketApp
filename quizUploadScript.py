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

#Author: Viraj Kadam
#Description: Entries for quizzes 3 and 4
questions2 = [
{
    #Question 1
    'text': 'What does a portfolio contain?',
    'answers': {
        'a': 'Your holdings',
        'b': 'Stock Buy Options',
        'c': 'Profits/Losses',
        'd': 'All of the above'
        },
    
    'correct': 'd'
},            
{
    #Question 2
    'text':'Should you take into account the historic value of the stock?',
    'answers': {
        'a': 'Yes',
        'b': 'No'
    },
    
    'correct': 'a'  
},

{ # Question 3
    'text' : 'Can someone in the United States invest in a company in China',
    'answers' : {
        'a' : 'Yes',
        'b' : 'No'
    },
    'correct' : 'a'
},
{ # Question 4
    'text' : 'Which of the following can affect the stock market?',
    'answers' : {
        'a' : 'Current Events',
        'b' : 'Interest Rates',
        'c' : 'Natural Calamaties',
        'd': 'All of the above'
    },
    'correct' : 'd'
},
{ # Question 5
    'text' : 'What is the ticker for Google?',
    'answers' : {
        'a' : 'G',
        'b' : 'GOOG',
        'c' : 'GE',
        'd' : 'GOO'
    },
    'correct' : 'b'
}, 
{ # Question 6
    'text' : 'How often should you keep track of your investments?',
    'answers' : {
        'a' : 'Once every week',
        'b' : 'Everyday',
        'c' : 'Every two weeks',
        'd' : 'Every month'
    },
    'correct' : 'b'
},
{ # Question 7
    'text' : 'What should you consider when buying a stock?',
    'answers' : {
        'a' : 'What the company does',
        'b' : 'How popular the company is',
        'c' : 'Is the company profitable', 
        'd' : 'What is the value of the stock',
        'e' : 'All of the above'
    },
    'correct' : 'e'
}, 
{ # Question 8
    'text' : 'Is trading more skill or luck?',
    'answers' : {
        'a' : 'Skills',
        'b' : 'Luck'
    },
    'correct' : 'b'
},
{ # Question 9
    'text' : 'What is the ticker for Ford Motor company?',
    'answers' : {
        'a' : 'FORD',
        'b' : 'FD',
        'c' : 'F',
        'd' : 'FO'
    },
    'correct' : 'c'
}
]
for entry in questions2:
    temp, tempID = db.collection('Quiz').add(entry)
    ids.append(tempID)

quiz3 = 'Quiz3'
db.collection('Quiz').document(quiz3).set(quiz)


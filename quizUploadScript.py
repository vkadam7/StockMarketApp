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
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
},
{ # Question 2
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
},
{ # Question 3
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
},
{ # Question 4
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
},
{ # Question 5
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
},
{ # Question 6
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
}, 
{ # Question 7
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
},
{ # Question 8
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
}, 
{ # Question 9
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
},
{ # Question 10
    'text' : '',
    'answers' : {
        'a' : '',
        'b' : '',
        'c' : ''
    },
    'correct' : 'a'
}]

ids = []
for entry in questions:
   temp = db.collection('Quiz').add(entry)
   ids.append(temp.id)

quiz = {
    'questionIds': ids
}

quizName = 'Tester'
db.collection('Quiz').document(quizName).set(quiz)
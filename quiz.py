from ast import Constant, Or
from mimetypes import init
from queue import Empty
from re import search
from statistics import mean, quantiles
from this import d
from time import daylight
import numpy as np
import pandas as pd
import firebase_admin
from firebase_admin import firestore
from google.cloud.firestore import ArrayUnion
import datetime

## Class for setting up quiz - Muneeb Khan (WIP!)
class Quiz:
    def __init__(self,db,req,useranswer):
        self.db = db
        self.quiz = req
        self.useranswer = useranswer
        self.data = Quiz.retrieve(self.db,self.quiz)
        if self.data != 'This data entry does not exist':
            self.question = self.data['question']
            self.answer = self.data['answer']
            tempData = self.data['question']
            self.question = tempData['question']
            self.answer = tempData['answer']
            self.a = tempData['a']
            self.b = tempData['b']
            self.c = tempData['c']

        else:
            print(self.data)
    
    def retrieveQuestions(self,db):
        return db.collection('Quiz').collection('question').stream()

    def listOfQuestions(self,db):
        questionList = []

        for entry in db.collection('Quiz').get():
            tempQuestions = entry.to_dict()
            questionList.append([tempQuestions['question'],tempQuestions['answer'],[tempQuestions['a'],tempQuestions['b'],tempQuestions['c']]])
        df = pd.DataFrame(questionList, columns=['buyOrSell','quantity','ticker','totalPrice'])
            
        return df

    def answerQuestions(self,db):
        if self.useranswer == self.answer:
            print("correct")
        else:
            print("incorrect")

    